from rest_framework import serializers

from .models import ActivityResourceType


class ActivityQuerySerializer(serializers.Serializer):
    """Validate activity query payload."""

    resource_type = serializers.ChoiceField(choices=ActivityResourceType.choices)


class ActivityLogResponseSerializer(serializers.Serializer):
    """Serialize activity log payload."""

    id = serializers.UUIDField()
    user_id = serializers.UUIDField(source="user.id")
    action = serializers.CharField()
    resource_type = serializers.CharField()
    resource_id = serializers.UUIDField()
    details = serializers.JSONField()
    created_at = serializers.DateTimeField()
