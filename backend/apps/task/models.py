from django.conf import settings
from django.db import models

from core.models import BaseModel


class TaskStatus(models.TextChoices):
    TODO = "To Do", "To Do"
    IN_PROGRESS = "In Progress", "In Progress"
    REVIEW = "Review", "Review"
    DONE = "Done", "Done"


class TaskPriority(models.TextChoices):
    LOW = "Low", "Low"
    MEDIUM = "Medium", "Medium"
    HIGH = "High", "High"


class Task(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey("project.Project", on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=32, choices=TaskStatus.choices, default=TaskStatus.TODO)
    priority = models.CharField(max_length=16, choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="assigned_tasks", blank=True)
    watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="watched_tasks", blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    actual_hours = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks")
    is_archived = models.BooleanField(default=False)


class SubTask(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)


class Attachment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    file_type = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.BigIntegerField(default=0)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_task_files")
    uploaded_at = models.DateTimeField(auto_now_add=True)
