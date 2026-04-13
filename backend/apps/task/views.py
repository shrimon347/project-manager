from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response
from apps.comment.serializers import CommentResponseSerializer

from .serializers import (
    SubTaskCreateSerializer,
    SubTaskUpdateSerializer,
    TaskAssigneesSerializer,
    TaskCommentCreateSerializer,
    TaskCreateSerializer,
    TaskPrioritySerializer,
    TaskWatchResponseSerializer,
    TaskActivityResponseSerializer,
    TaskResponseSerializer,
    TaskStatusSerializer,
    TaskUpdateFieldSerializer,
)
from .services import TaskService


@extend_schema(tags=["Tasks"])
class TaskCreateView(APIView):
    """Handle task creation endpoint.

    Parameters:
    - request: authenticated request with task payload
    - project_id: project UUID

    Returns:
    - standardized success response with created task
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskCreateSerializer

    def post(self, request, project_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = TaskService.create_task(user=request.user, project_id=project_id, **serializer.validated_data)
        response_serializer = TaskResponseSerializer(instance=task)
        return success_response(
            message="Task created successfully.",
            data={"task": response_serializer.data},
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Tasks"])
class TaskDetailView(APIView):
    """Handle task detail endpoint.

    Parameters:
    - request: authenticated request
    - task_id: task UUID

    Returns:
    - standardized success response with task details
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskResponseSerializer

    def get(self, request, task_id):
        task = TaskService.get_task_by_id(user=request.user, task_id=task_id)
        serializer = self.serializer_class(instance=task)
        return success_response(
            message="Task fetched successfully.",
            data={"task": serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Tasks"])
class TaskMyTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskResponseSerializer

    def get(self, request):
        tasks = TaskService.get_my_tasks(user=request.user)
        serializer = self.serializer_class(instance=tasks, many=True)
        return success_response(
            message="My tasks fetched successfully.",
            data={"tasks": serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Tasks"])
class TaskTitleUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskUpdateFieldSerializer

    def put(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = TaskService.update_title(user=request.user, task_id=task_id, value=serializer.validated_data["value"])
        return success_response(message="Task title updated successfully.", data={"task": task}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskDescriptionUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskUpdateFieldSerializer

    def put(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = TaskService.update_description(user=request.user, task_id=task_id, value=serializer.validated_data["value"])
        return success_response(message="Task description updated successfully.", data={"task": task}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskStatusSerializer

    def put(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = TaskService.update_status(user=request.user, task_id=task_id, value=serializer.validated_data["status"])
        return success_response(message="Task status updated successfully.", data={"task": task}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskPriorityUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskPrioritySerializer

    def put(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = TaskService.update_priority(user=request.user, task_id=task_id, value=serializer.validated_data["priority"])
        return success_response(message="Task priority updated successfully.", data={"task": task}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskAssigneesUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskAssigneesSerializer

    def put(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = TaskService.update_assignees(user=request.user, task_id=task_id, value=serializer.validated_data["value"])
        return success_response(message="Task assignees updated successfully.", data={"task": task}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskSubTaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubTaskCreateSerializer

    def post(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        subtask = TaskService.add_subtask(user=request.user, task_id=task_id, title=serializer.validated_data["title"])
        return success_response(message="Subtask added successfully.", data={"subtask": subtask}, status_code=status.HTTP_201_CREATED)


@extend_schema(tags=["Tasks"])
class TaskSubTaskUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubTaskUpdateSerializer

    def put(self, request, task_id, subtask_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        subtask = TaskService.update_subtask(
            user=request.user,
            task_id=task_id,
            subtask_id=subtask_id,
            **serializer.validated_data,
        )
        return success_response(message="Subtask updated successfully.", data={"subtask": subtask}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskCommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskCommentCreateSerializer

    def post(self, request, task_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = TaskService.add_comment(user=request.user, task_id=task_id, **serializer.validated_data)
        return success_response(message="Comment added successfully.", data={"comment": comment}, status_code=status.HTTP_201_CREATED)


@extend_schema(tags=["Tasks"])
class TaskCommentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentResponseSerializer

    def get(self, request, task_id):
        comments = TaskService.get_comments(user=request.user, task_id=task_id)
        serializer = self.serializer_class(instance=comments, many=True)
        return success_response(message="Comments fetched successfully.", data={"comments": serializer.data}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskWatchToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskWatchResponseSerializer

    def post(self, request, task_id):
        result = TaskService.toggle_watch(user=request.user, task_id=task_id)
        serializer = self.serializer_class(instance=result)
        return success_response(message="Watch state updated successfully.", data=serializer.data, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskAchievedToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskResponseSerializer

    def post(self, request, task_id):
        task = TaskService.toggle_achieved(user=request.user, task_id=task_id)
        serializer = self.serializer_class(instance=task)
        return success_response(message="Task archive state updated successfully.", data={"task": serializer.data}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Tasks"])
class TaskActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskActivityResponseSerializer

    def get(self, request, task_id):
        activity = TaskService.get_task_activity(user=request.user, task_id=task_id)
        serializer = self.serializer_class(instance=activity, many=True)
        return success_response(message="Task activity fetched successfully.", data={"activity": serializer.data}, status_code=status.HTTP_200_OK)
