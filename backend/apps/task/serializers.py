from rest_framework import serializers

from .models import TaskPriority, TaskStatus


class TaskCreateSerializer(serializers.Serializer):
    """Validate task creation payload."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=TaskStatus.choices, required=False, default=TaskStatus.TODO)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, required=False, default=TaskPriority.MEDIUM)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    estimated_hours = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, allow_null=True)
    actual_hours = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, allow_null=True)
    tags = serializers.JSONField(required=False, default=list)
    assignee_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)


class TaskUpdateFieldSerializer(serializers.Serializer):
    """Validate generic task update field payload."""

    value = serializers.CharField()


class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=TaskStatus.choices)


class TaskPrioritySerializer(serializers.Serializer):
    priority = serializers.ChoiceField(choices=TaskPriority.choices)


class TaskAssigneesSerializer(serializers.Serializer):
    value = serializers.ListField(child=serializers.UUIDField(), default=list)


class SubTaskCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)


class SubTaskUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    completed = serializers.BooleanField(required=False)


class TaskCommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField()
    mentions = serializers.JSONField(required=False, default=list)
    reactions = serializers.JSONField(required=False, default=list)
    attachments = serializers.JSONField(required=False, default=list)


class TaskResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField()
    priority = serializers.CharField()
    project_id = serializers.UUIDField()
    assignee_ids = serializers.ListField(child=serializers.UUIDField())
    watcher_ids = serializers.ListField(child=serializers.UUIDField())
    due_date = serializers.DateTimeField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    estimated_hours = serializers.DecimalField(max_digits=7, decimal_places=2, allow_null=True)
    actual_hours = serializers.DecimalField(max_digits=7, decimal_places=2, allow_null=True)
    tags = serializers.JSONField()
    created_by = serializers.UUIDField()
    is_archived = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class TaskWatchResponseSerializer(serializers.Serializer):
    """Serialize watch-toggle response payload."""

    task_id = serializers.UUIDField()
    watched = serializers.BooleanField()


class TaskActivityResponseSerializer(serializers.Serializer):
    """Serialize task activity response payload."""

    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    action = serializers.CharField()
    resource_type = serializers.CharField()
    resource_id = serializers.UUIDField()
    details = serializers.JSONField()
    created_at = serializers.DateTimeField()
