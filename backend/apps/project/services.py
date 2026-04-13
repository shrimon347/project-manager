from django.db import transaction

from apps.activity.models import ActivityAction, ActivityResourceType
from apps.activity.services import ActivityService
from core.exceptions import ForbiddenException, NotFoundException

from .models import Project, ProjectMember, ProjectMemberRole


class ProjectService:
    """Application service for project workflows."""

    @staticmethod
    @transaction.atomic
    def create_project(*, user, workspace_id, **payload):
        """Create a workspace project and attach creator as manager.

        Parameters:
        - user: authenticated user instance
        - workspace_id: target workspace UUID
        - payload: validated project fields

        Returns:
        - dict project payload
        """
        from apps.workspaces.models import Workspace, WorkspaceMember

        workspace = Workspace.objects.filter(id=workspace_id).first()
        if not workspace:
            raise NotFoundException(detail="Workspace not found.", code="workspace_not_found")
        if not WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            raise ForbiddenException(detail="Only workspace members can create projects.", code="project_create_forbidden")

        project = Project.objects.create(workspace=workspace, created_by=user, **payload)
        ProjectMember.objects.create(project=project, user=user, role=ProjectMemberRole.MANAGER)
        workspace.projects.add(project)
        ActivityService.record_activity(
            user=user,
            action=ActivityAction.PROJECT_CREATED,
            resource_type=ActivityResourceType.PROJECT,
            resource_id=project.id,
            details={"workspace_id": str(workspace.id), "title": project.title},
        )
        return ProjectService.get_project_details(user=user, project_id=project.id)

    @staticmethod
    def get_project_details(*, user, project_id):
        """Get project details for workspace member.

        Parameters:
        - user: authenticated user instance
        - project_id: target project UUID

        Returns:
        - dict project payload
        """
        from apps.workspaces.models import WorkspaceMember

        project = Project.objects.select_related("workspace", "created_by").filter(id=project_id).first()
        if not project:
            raise NotFoundException(detail="Project not found.", code="project_not_found")
        if not WorkspaceMember.objects.filter(workspace=project.workspace, user=user).exists():
            raise ForbiddenException(detail="Only workspace members can access project details.", code="project_access_denied")

        memberships = ProjectMember.objects.select_related("user").filter(project=project)
        return {
            "id": str(project.id),
            "title": project.title,
            "description": project.description,
            "workspace_id": str(project.workspace_id),
            "status": project.status,
            "start_date": project.start_date,
            "due_date": project.due_date,
            "progress": project.progress,
            "created_by": str(project.created_by_id),
            "is_archived": project.is_archived,
            "members": [
                {
                    "user": {
                        "id": str(row.user.id),
                        "email": row.user.email,
                        "name": row.user.name,
                    },
                    "role": row.role,
                    "tags": row.tags,
                }
                for row in memberships
            ],
            "created_at": project.created_at,
        }

    @staticmethod
    def get_project_tasks(*, user, project_id):
        """Get project tasks for authorized workspace member.

        Parameters:
        - user: authenticated user instance
        - project_id: target project UUID

        Returns:
        - list of task dictionaries
        """
        project = ProjectService._get_authorized_project(user=user, project_id=project_id)
        return [
            {
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "is_archived": task.is_archived,
            }
            for task in project.tasks.all().order_by("-created_at")
        ]

    @staticmethod
    def _get_authorized_project(*, user, project_id):
        from apps.workspaces.models import WorkspaceMember

        project = Project.objects.select_related("workspace").filter(id=project_id).first()
        if not project:
            raise NotFoundException(detail="Project not found.", code="project_not_found")
        if not WorkspaceMember.objects.filter(workspace=project.workspace, user=user).exists():
            raise ForbiddenException(detail="Project access denied.", code="project_access_denied")
        return project
