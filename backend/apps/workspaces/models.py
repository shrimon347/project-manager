import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class WorkspaceRole(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"
    VIEWER = "viewer", "Viewer"


class Workspace(BaseModel):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=16, default="#FF5733")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_workspaces",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="WorkspaceMember",
        related_name="workspaces",
    )

    class Meta:
        ordering = ["-created_at"]


class WorkspaceMember(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="workspace_memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_memberships")
    role = models.CharField(max_length=32, choices=WorkspaceRole.choices, default=WorkspaceRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["workspace", "user"], name="uniq_workspace_member"),
        ]


class WorkspaceInvite(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="invites")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_invites_sent")
    email = models.EmailField()
    role = models.CharField(max_length=32, choices=WorkspaceRole.choices, default=WorkspaceRole.MEMBER)
    token_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace", "email", "accepted_at"]),
        ]

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def issue_token(cls, *, workspace, invited_by, email, role, expires_in_hours=72):
        raw_token = secrets.token_urlsafe(32)
        token_hash = cls.hash_token(raw_token)
        invite = cls.objects.create(
            workspace=workspace,
            invited_by=invited_by,
            email=email,
            role=role,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=expires_in_hours),
        )
        return invite, raw_token

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
