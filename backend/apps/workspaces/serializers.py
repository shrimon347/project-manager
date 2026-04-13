from rest_framework import serializers

from .models import WorkspaceRole


class WorkspaceCreateSerializer(serializers.Serializer):
    """Validate workspace creation payload for service layer usage."""

    name = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    color = serializers.CharField(max_length=16, required=False, default="#FF5733")

    def validate_name(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Workspace name is required.")
        return trimmed


class WorkspaceInviteSerializer(serializers.Serializer):
    """Validate invite payload for service layer usage."""

    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=WorkspaceRole.choices, default=WorkspaceRole.MEMBER)

    def validate_email(self, value):
        return value.strip().lower()


class WorkspaceInviteTokenSerializer(serializers.Serializer):
    """Validate invite-token acceptance payload for service layer usage."""

    token = serializers.CharField()


class WorkspaceMemberResponseSerializer(serializers.Serializer):
    """Serialize workspace member payload for response validation."""

    id = serializers.UUIDField()
    email = serializers.EmailField()
    name = serializers.CharField(allow_blank=True, allow_null=True)
    role = serializers.ChoiceField(choices=WorkspaceRole.choices)
    joined_at = serializers.DateTimeField()


class WorkspaceSummaryResponseSerializer(serializers.Serializer):
    """Serialize workspace summary payload for response validation."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    color = serializers.CharField()
    owner_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=WorkspaceRole.choices, allow_null=True)
    created_at = serializers.DateTimeField()


class WorkspaceDetailResponseSerializer(WorkspaceSummaryResponseSerializer):
    """Serialize workspace detail payload for response validation."""

    members = WorkspaceMemberResponseSerializer(many=True)


class WorkspaceProjectResponseSerializer(serializers.Serializer):
    """Serialize workspace project payload for response validation."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField(allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField()


class WorkspaceStatsResponseSerializer(serializers.Serializer):
    """Serialize workspace stats payload for response validation."""

    workspace_id = serializers.UUIDField()
    member_count = serializers.IntegerField()
    project_count = serializers.IntegerField()
    projects_by_status = serializers.DictField(child=serializers.IntegerField())
