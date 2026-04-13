import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from core.exceptions import ConflictException, ForbiddenException, NotFoundException, UnauthorizedException

from .models import Workspace, WorkspaceInvite, WorkspaceMember, WorkspaceRole

logger = logging.getLogger("app.request")
User = get_user_model()


class WorkspaceService:
    """Application service for workspace and invitation workflows."""

    @staticmethod
    @transaction.atomic
    def create_workspace(*, user, name, description=None, color="#FF5733"):
        """Create workspace and attach owner as member.

        Parameters:
        - user: authenticated user instance
        - name: workspace name
        - description: optional workspace description
        - color: optional workspace color hex value

        Returns:
        - dict payload with workspace details
        """
        workspace = Workspace.objects.create(owner=user, name=name, description=description, color=color)
        WorkspaceMember.objects.create(workspace=workspace, user=user, role=WorkspaceRole.OWNER)
        WorkspaceService._log_activity("workspace_created", user_id=str(user.id), workspace_id=str(workspace.id))
        return WorkspaceService._workspace_payload(workspace, current_user=user)

    @staticmethod
    def list_user_workspaces(*, user):
        """Return all workspaces where user is a member.

        Parameters:
        - user: authenticated user instance

        Returns:
        - list of workspace payloads
        """
        workspaces = (
            Workspace.objects.filter(workspace_memberships__user=user)
            .select_related("owner")
            .distinct()
            .order_by("-created_at")
        )
        return [WorkspaceService._workspace_payload(ws, current_user=user) for ws in workspaces]

    @staticmethod
    def get_workspace_details(*, user, workspace_id):
        """Return workspace details with member list.

        Parameters:
        - user: authenticated user instance
        - workspace_id: target workspace UUID

        Returns:
        - dict workspace details including members
        """
        workspace = WorkspaceService._get_member_workspace(user=user, workspace_id=workspace_id)
        memberships = workspace.workspace_memberships.select_related("user").all()
        return {
            **WorkspaceService._workspace_payload(workspace, current_user=user),
            "members": [
                {
                    "id": str(member.user.id),
                    "email": member.user.email,
                    "name": member.user.name,
                    "role": member.role,
                    "joined_at": member.joined_at,
                }
                for member in memberships
            ],
        }

    @staticmethod
    def get_workspace_projects(*, user, workspace_id):
        """Return projects under workspace after membership check.

        Parameters:
        - user: authenticated user instance
        - workspace_id: target workspace UUID

        Returns:
        - list of project payloads
        """
        workspace = WorkspaceService._get_member_workspace(user=user, workspace_id=workspace_id)
        if not hasattr(workspace, "projects"):
            return []
        projects = workspace.projects.all().order_by("-created_at")
        return [
            {
                "id": str(project.id),
                "name": getattr(project, "name", ""),
                "status": getattr(project, "status", None),
                "created_at": project.created_at,
            }
            for project in projects
        ]

    @staticmethod
    def get_workspace_stats(*, user, workspace_id):
        """Return workspace stats aggregation data.

        Parameters:
        - user: authenticated user instance
        - workspace_id: target workspace UUID

        Returns:
        - dict containing aggregated stats
        """
        workspace = WorkspaceService._get_member_workspace(user=user, workspace_id=workspace_id)
        member_count = workspace.workspace_memberships.count()
        project_count = workspace.projects.count() if hasattr(workspace, "projects") else 0
        projects_by_status = {}
        if hasattr(workspace, "projects"):
            status_rows = (
                workspace.projects.values("status")
                .annotate(total=Count("id"))
                .order_by()
            )
            projects_by_status = {row["status"] or "unknown": row["total"] for row in status_rows}
        return {
            "workspace_id": str(workspace.id),
            "member_count": member_count,
            "project_count": project_count,
            "projects_by_status": projects_by_status,
        }

    @staticmethod
    @transaction.atomic
    def invite_user(*, user, workspace_id, email, role):
        """Invite user to workspace and emit invite token email.

        Parameters:
        - user: authenticated user instance (inviter)
        - workspace_id: target workspace UUID
        - email: invitee email
        - role: membership role for invitee

        Returns:
        - dict invite metadata
        """
        workspace = WorkspaceService._get_member_workspace(user=user, workspace_id=workspace_id)
        inviter_membership = WorkspaceService._get_membership(workspace=workspace, user=user)
        if inviter_membership.role not in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}:
            raise ForbiddenException(detail="Only owner/admin can invite members.", code="invite_forbidden")

        existing_user = User.objects.filter(email=email).first()
        if existing_user and WorkspaceMember.objects.filter(workspace=workspace, user=existing_user).exists():
            raise ConflictException(detail="User is already a workspace member.", errors={"email": "Already a member."})

        active_invite_exists = WorkspaceInvite.objects.filter(
            workspace=workspace,
            email=email,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now(),
        ).exists()
        if active_invite_exists:
            raise ConflictException(detail="An active invite already exists.", errors={"email": "Duplicate invite."})

        invite, _ = WorkspaceInvite.issue_token(
            workspace=workspace,
            invited_by=user,
            email=email,
            role=role,
        )
        jwt_token = WorkspaceService._build_invite_jwt(
            invite_id=str(invite.id),
            user_id=str(existing_user.id) if existing_user else None,
            workspace_id=str(workspace.id),
            role=role,
            expires_at=invite.expires_at,
        )
        WorkspaceService._send_invite_email(email=email, token=jwt_token, workspace_name=workspace.name)
        WorkspaceService._log_activity("workspace_invite_created", user_id=str(user.id), workspace_id=str(workspace.id))
        return {
            "invite_id": str(invite.id),
            "email": email,
            "role": role,
            "expires_at": invite.expires_at,
        }

    @staticmethod
    @transaction.atomic
    def accept_invite(*, user, workspace_id):
        """Accept direct invite by adding authenticated user to workspace.

        Parameters:
        - user: authenticated user instance
        - workspace_id: target workspace UUID

        Returns:
        - dict containing workspace member context
        """
        workspace = Workspace.objects.filter(id=workspace_id).select_related("owner").first()
        if not workspace:
            raise NotFoundException(detail="Workspace not found.", code="workspace_not_found")
        if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            raise ConflictException(detail="You are already a member of this workspace.")

        invite = WorkspaceInvite.objects.filter(
            workspace=workspace,
            email=user.email,
            accepted_at__isnull=True,
        ).order_by("-created_at").first()
        if not invite:
            raise NotFoundException(detail="No pending invite found for user.", code="invite_not_found")
        if invite.is_expired():
            raise UnauthorizedException(detail="Invite has expired.", code="invite_expired")

        WorkspaceMember.objects.create(workspace=workspace, user=user, role=invite.role)
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["accepted_at", "updated_at"])
        WorkspaceService._log_activity("workspace_invite_accepted", user_id=str(user.id), workspace_id=str(workspace.id))
        return WorkspaceService._workspace_payload(workspace, current_user=user)

    @staticmethod
    @transaction.atomic
    def accept_invite_via_token(*, user, token):
        """Accept workspace invite using JWT token payload.

        Parameters:
        - user: authenticated user instance
        - token: invite JWT

        Returns:
        - dict containing joined workspace payload
        """
        payload = WorkspaceService._decode_invite_jwt(token=token)
        invite = WorkspaceInvite.objects.filter(id=payload["invite_id"]).select_related("workspace").first()
        if not invite:
            raise NotFoundException(detail="Invite not found.", code="invite_not_found")
        if invite.accepted_at:
            raise ConflictException(detail="Invite already accepted.", code="invite_already_used")
        if invite.is_expired():
            raise UnauthorizedException(detail="Invite has expired.", code="invite_expired")
        if invite.email != user.email:
            raise ForbiddenException(detail="Invite token email does not match current user.", code="invite_user_mismatch")
        if WorkspaceMember.objects.filter(workspace=invite.workspace, user=user).exists():
            raise ConflictException(detail="User already in workspace.", code="already_member")

        WorkspaceMember.objects.create(workspace=invite.workspace, user=user, role=payload["role"])
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["accepted_at", "updated_at"])
        WorkspaceService._log_activity("workspace_invite_accepted_token", user_id=str(user.id), workspace_id=str(invite.workspace.id))
        return WorkspaceService._workspace_payload(invite.workspace, current_user=user)

    @staticmethod
    def _workspace_payload(workspace, *, current_user):
        membership = WorkspaceMember.objects.filter(workspace=workspace, user=current_user).first()
        return {
            "id": str(workspace.id),
            "name": workspace.name,
            "description": workspace.description,
            "color": workspace.color,
            "owner_id": str(workspace.owner_id),
            "role": membership.role if membership else None,
            "created_at": workspace.created_at,
        }

    @staticmethod
    def _get_member_workspace(*, user, workspace_id):
        workspace = Workspace.objects.filter(id=workspace_id).select_related("owner").first()
        if not workspace:
            raise NotFoundException(detail="Workspace not found.", code="workspace_not_found")
        if not WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            raise ForbiddenException(detail="Only workspace members can access this resource.", code="workspace_access_denied")
        return workspace

    @staticmethod
    def _get_membership(*, workspace, user):
        membership = WorkspaceMember.objects.filter(workspace=workspace, user=user).first()
        if not membership:
            raise ForbiddenException(detail="You are not a workspace member.", code="workspace_access_denied")
        return membership

    @staticmethod
    def _build_invite_jwt(*, invite_id, user_id, workspace_id, role, expires_at):
        token = AccessToken()
        token.set_exp(from_time=timezone.now(), lifetime=expires_at - timezone.now())
        token["invite_id"] = invite_id
        token["user_id"] = user_id
        token["workspace_id"] = workspace_id
        token["role"] = role
        token["expiry"] = int(expires_at.timestamp())
        return str(token)

    @staticmethod
    def _decode_invite_jwt(*, token):
        try:
            payload = AccessToken(token)
        except TokenError as exc:
            raise UnauthorizedException(detail="Invalid invite token.", code="invalid_invite_token") from exc

        required_keys = {"invite_id", "workspace_id", "role", "expiry"}
        if not required_keys.issubset(set(payload.keys())):
            raise UnauthorizedException(detail="Malformed invite token.", code="invalid_invite_token")
        if timezone.now().timestamp() >= int(payload["expiry"]):
            raise UnauthorizedException(detail="Invite token has expired.", code="invite_expired")
        return payload

    @staticmethod
    def _send_invite_email(*, email, token, workspace_name):
        logger.info("[MOCK EMAIL] invite email=%s workspace=%s token=%s", email, workspace_name, token)

    @staticmethod
    def _log_activity(event, **metadata):
        logger.info("activity=%s meta=%s", event, metadata)
