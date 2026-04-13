from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response

from .serializers import CommentCreateSerializer, CommentResponseSerializer
from .services import CommentService


@extend_schema(tags=["Comments"])
class CommentByTaskView(APIView):
    """Handle direct task comment create/list endpoints.

    Parameters:
    - request: authenticated request
    - task_id: task UUID

    Returns:
    - standardized success response with comment payload(s)
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentCreateSerializer

    def post(self, request, task_id):
        from apps.task.services import TaskService

        task = TaskService._authorized_task(user=request.user, task_id=task_id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = CommentService.add_comment(user=request.user, task=task, **serializer.validated_data)
        response_serializer = CommentResponseSerializer(instance=comment)
        return success_response(
            message="Comment added successfully.",
            data={"comment": response_serializer.data},
            status_code=status.HTTP_201_CREATED,
        )

    def get(self, request, task_id):
        from apps.task.services import TaskService

        task = TaskService._authorized_task(user=request.user, task_id=task_id)
        comments = CommentService.get_comments(task=task)
        response_serializer = CommentResponseSerializer(instance=comments, many=True)
        return success_response(
            message="Comments fetched successfully.",
            data={"comments": response_serializer.data},
            status_code=status.HTTP_200_OK,
        )
