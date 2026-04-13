from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response

from .serializers import ActivityLogResponseSerializer
from .services import ActivityService


@extend_schema(tags=["Activity"])
class ActivityByResourceView(APIView):
    """Handle activity list by resource endpoint.

    Parameters:
    - request: authenticated request
    - resource_id: target resource UUID

    Returns:
    - standardized success response with activity records
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivityLogResponseSerializer

    def get(self, request, resource_id):
        logs = ActivityService.get_by_resource(resource_id=resource_id)
        serializer = self.serializer_class(instance=logs, many=True)
        return success_response(
            message="Activity fetched successfully.",
            data={"activity": serializer.data},
            status_code=status.HTTP_200_OK,
        )
