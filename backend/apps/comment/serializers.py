from rest_framework import serializers


class CommentCreateSerializer(serializers.Serializer):
    """Validate task comment creation payload."""

    text = serializers.CharField()
    mentions = serializers.JSONField(required=False, default=list)
    reactions = serializers.JSONField(required=False, default=list)
    attachments = serializers.JSONField(required=False, default=list)


class CommentResponseSerializer(serializers.Serializer):
    """Serialize task comment response payload."""

    id = serializers.UUIDField()
    text = serializers.CharField()
    task_id = serializers.UUIDField()
    author_id = serializers.UUIDField()
    mentions = serializers.JSONField()
    reactions = serializers.JSONField()
    attachments = serializers.JSONField()
    is_edited = serializers.BooleanField()
    created_at = serializers.DateTimeField()
