from rest_framework import serializers

from .models import ProjectMemberRole, ProjectStatus


class ProjectCreateSerializer(serializers.Serializer):
    """Validate project creation payload."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=ProjectStatus.choices, required=False, default=ProjectStatus.PLANNING)
    start_date = serializers.DateField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    progress = serializers.IntegerField(required=False, min_value=0, max_value=100, default=0)

    def validate_title(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Project title is required.")
        return trimmed


class ProjectMemberResponseSerializer(serializers.Serializer):
    """Serialize project member response payload."""

    user_id = serializers.UUIDField(source="user.id")
    email = serializers.EmailField(source="user.email")
    name = serializers.CharField(source="user.name", allow_blank=True, allow_null=True)
    role = serializers.ChoiceField(choices=ProjectMemberRole.choices)
    tags = serializers.JSONField()


class ProjectResponseSerializer(serializers.Serializer):
    """Serialize project response payload."""

    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    workspace_id = serializers.UUIDField()
    status = serializers.CharField()
    start_date = serializers.DateField(allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    progress = serializers.IntegerField()
    created_by = serializers.UUIDField()
    is_archived = serializers.BooleanField()
    members = ProjectMemberResponseSerializer(many=True)
    created_at = serializers.DateTimeField()


class ProjectTaskResponseSerializer(serializers.Serializer):
    """Serialize project-task listing payload."""

    id = serializers.UUIDField()
    title = serializers.CharField()
    status = serializers.CharField()
    priority = serializers.CharField()
    due_date = serializers.DateTimeField(allow_null=True)
    is_archived = serializers.BooleanField()
