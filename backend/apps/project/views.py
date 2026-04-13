from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response

from .serializers import ProjectCreateSerializer, ProjectResponseSerializer, ProjectTaskResponseSerializer
from .services import ProjectService


@extend_schema(tags=["Projects"])
class ProjectCreateView(APIView):
    """Handle project creation endpoint.

    Parameters:
    - request: authenticated request with validated project payload
    - workspace_id: workspace UUID

    Returns:
    - standardized success response with project payload
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectCreateSerializer

    def post(self, request, workspace_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = ProjectService.create_project(user=request.user, workspace_id=workspace_id, **serializer.validated_data)
        response_serializer = ProjectResponseSerializer(instance=project)
        return success_response(
            message="Project created successfully.",
            data={"project": response_serializer.data},
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Projects"])
class ProjectDetailView(APIView):
    """Handle project detail endpoint.

    Parameters:
    - request: authenticated request
    - project_id: project UUID

    Returns:
    - standardized success response with project details
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectResponseSerializer

    def get(self, request, project_id):
        project = ProjectService.get_project_details(user=request.user, project_id=project_id)
        serializer = self.serializer_class(instance=project)
        return success_response(
            message="Project fetched successfully.",
            data={"project": serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Projects"])
class ProjectTasksView(APIView):
    """Handle project task listing endpoint.

    Parameters:
    - request: authenticated request
    - project_id: project UUID

    Returns:
    - standardized success response with project tasks
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectTaskResponseSerializer

    def get(self, request, project_id):
        tasks = ProjectService.get_project_tasks(user=request.user, project_id=project_id)
        serializer = self.serializer_class(instance=tasks, many=True)
        return success_response(
            message="Project tasks fetched successfully.",
            data={"tasks": serializer.data},
            status_code=status.HTTP_200_OK,
        )
