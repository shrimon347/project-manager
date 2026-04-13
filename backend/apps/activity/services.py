from apps.activity.models import ActivityLog


class ActivityService:
    """Application service for recording and reading activity logs."""

    @staticmethod
    def record_activity(*, user, action, resource_type, resource_id, details=None):
        """Record a single activity row.

        Parameters:
        - user: actor user instance
        - action: activity action enum value
        - resource_type: resource category
        - resource_id: UUID of resource
        - details: optional metadata dictionary

        Returns:
        - ActivityLog instance
        """
        return ActivityLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )

    @staticmethod
    def get_by_resource(*, resource_id):
        """Get all activity records by resource UUID.

        Parameters:
        - resource_id: UUID of resource

        Returns:
        - queryset of ActivityLog
        """
        return ActivityLog.objects.select_related("user").filter(resource_id=resource_id).order_by("-created_at")
