from django.conf import settings
from django.db import models

from core.models import BaseModel


class Comment(BaseModel):
    text = models.TextField()
    task = models.ForeignKey("task.Task", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments")
    mentions = models.JSONField(default=list, blank=True)
    reactions = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    is_edited = models.BooleanField(default=False)
