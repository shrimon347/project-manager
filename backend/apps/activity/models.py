from django.conf import settings
from django.db import models

from core.models import BaseModel


class ActivityResourceType(models.TextChoices):
    TASK = "Task", "Task"
    PROJECT = "Project", "Project"
    WORKSPACE = "Workspace", "Workspace"
    COMMENT = "Comment", "Comment"
    USER = "User", "User"


class ActivityAction(models.TextChoices):
    TASK_CREATED = "TASK_CREATED", "Task Created"
    TASK_UPDATED = "TASK_UPDATED", "Task Updated"
    TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED", "Task Status Changed"
    TASK_PRIORITY_CHANGED = "TASK_PRIORITY_CHANGED", "Task Priority Changed"
    TASK_ASSIGNEES_CHANGED = "TASK_ASSIGNEES_CHANGED", "Task Assignees Changed"
    TASK_ARCHIVED = "TASK_ARCHIVED", "Task Archived"
    TASK_UNARCHIVED = "TASK_UNARCHIVED", "Task Unarchived"
    SUBTASK_CREATED = "SUBTASK_CREATED", "Subtask Created"
    SUBTASK_UPDATED = "SUBTASK_UPDATED", "Subtask Updated"
    COMMENT_ADDED = "COMMENT_ADDED", "Comment Added"
    WATCHER_ADDED = "WATCHER_ADDED", "Watcher Added"
    WATCHER_REMOVED = "WATCHER_REMOVED", "Watcher Removed"
    PROJECT_CREATED = "PROJECT_CREATED", "Project Created"
    WORKSPACE_CREATED = "WORKSPACE_CREATED", "Workspace Created"


class ActivityLog(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=64, choices=ActivityAction.choices)
    resource_type = models.CharField(max_length=32, choices=ActivityResourceType.choices)
    resource_id = models.UUIDField(db_index=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
