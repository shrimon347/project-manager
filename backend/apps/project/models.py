from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseModel


class ProjectStatus(models.TextChoices):
    PLANNING = "Planning", "Planning"
    IN_PROGRESS = "In Progress", "In Progress"
    ON_HOLD = "On Hold", "On Hold"
    COMPLETED = "Completed", "Completed"
    CANCELLED = "Cancelled", "Cancelled"


class ProjectMemberRole(models.TextChoices):
    MANAGER = "manager", "Manager"
    CONTRIBUTOR = "contributor", "Contributor"
    VIEWER = "viewer", "Viewer"


class Project(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="workspace_projects")
    status = models.CharField(max_length=32, choices=ProjectStatus.choices, default=ProjectStatus.PLANNING)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    progress = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_projects")
    is_archived = models.BooleanField(default=False)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="ProjectMember", related_name="projects")


class ProjectMember(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_memberships")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_memberships")
    role = models.CharField(max_length=32, choices=ProjectMemberRole.choices, default=ProjectMemberRole.CONTRIBUTOR)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "project"], name="uniq_project_member"),
        ]
