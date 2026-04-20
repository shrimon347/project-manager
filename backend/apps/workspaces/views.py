from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response

from .serializers import (
    WorkspaceCreateSerializer,
    WorkspaceDetailResponseSerializer,
    WorkspaceInviteSerializer,
    WorkspaceInviteTokenSerializer,
    WorkspaceListSerializer,
    WorkspaceProjectResponseSerializer,
    WorkspaceStatsResponseSerializer,
    WorkspaceSummaryResponseSerializer,
)
from .services import WorkspaceService


@extend_schema(tags=["Workspaces"])
class WorkspaceCollectionView(APIView):
    """Handle workspace create and current-user listing endpoints.

    Parameters:
    - request: authenticated API request

    Returns:
    - create: created workspace payload
    - list: user workspace list
    """

    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method == "POST":
            return WorkspaceCreateSerializer
        return WorkspaceListSerializer

    @extend_schema(operation_id="workspaces_create")
    def post(self, request):
        """Create a workspace and add requester as owner-member.

        Parameters:
        - request: authenticated request with workspace payload

        Returns:
        - standardized success response with workspace data
        """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        workspace = WorkspaceService.create_workspace(user=request.user, **serializer.validated_data)
        return success_response(
            message="Workspace created successfully.",
            data={"workspace": workspace},
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(operation_id="workspaces_list")
    def get(self, request):
        """Get all workspaces for the authenticated user.

        Parameters:
        - request: authenticated request

        Returns:
        - standardized success response with workspace list
        """
        workspaces = WorkspaceService.list_user_workspaces(user=request.user)
        serializer = WorkspaceListSerializer(workspaces, many=True)

        return success_response(
            message="Workspaces fetched successfully.",
            data={"workspaces": serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Workspaces"])
class WorkspaceDetailView(APIView):
    """Handle workspace detail endpoint.

    Parameters:
    - request: authenticated API request
    - workspace_id: workspace UUID

    Returns:
    - standardized success response with workspace details and members
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceDetailResponseSerializer

    @extend_schema(operation_id="workspaces_retrieve")
    def get(self, request, workspace_id):
        details = WorkspaceService.get_workspace_details(user=request.user, workspace_id=workspace_id)
        response_serializer = self.serializer_class(instance=details)
        return success_response(
            message="Workspace details fetched successfully.",
            data={"workspace": response_serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Workspaces"])
class WorkspaceProjectsView(APIView):
    """Handle workspace projects endpoint with membership access control.

    Parameters:
    - request: authenticated API request
    - workspace_id: workspace UUID

    Returns:
    - standardized success response with project list
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceProjectResponseSerializer

    @extend_schema(operation_id="workspaces_projects_list")
    def get(self, request, workspace_id):
        projects = WorkspaceService.get_workspace_projects(user=request.user, workspace_id=workspace_id)
        response_serializer = self.serializer_class(instance=projects, many=True)
        return success_response(
            message="Workspace projects fetched successfully.",
            data={"projects": response_serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Workspaces"])
class WorkspaceStatsView(APIView):
    """Handle workspace stats endpoint.

    Parameters:
    - request: authenticated API request
    - workspace_id: workspace UUID

    Returns:
    - standardized success response with aggregated workspace stats
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceStatsResponseSerializer

    @extend_schema(operation_id="workspaces_stats_retrieve")
    def get(self, request, workspace_id):
        stats_payload = WorkspaceService.get_workspace_stats(user=request.user, workspace_id=workspace_id)
        response_serializer = self.serializer_class(instance=stats_payload)
        return success_response(
            message="Workspace stats fetched successfully.",
            data={"stats": response_serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Workspaces"])
class WorkspaceInviteView(APIView):
    """Handle workspace invitation creation endpoint.

    Parameters:
    - request: authenticated API request
    - workspace_id: workspace UUID

    Returns:
    - standardized success response with invite metadata
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceInviteSerializer

    def post(self, request, workspace_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = WorkspaceService.invite_user(
            user=request.user,
            workspace_id=workspace_id,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
        )
        return success_response(
            message="Workspace invite sent successfully.",
            data={"invite": invite},
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Workspaces"])
class WorkspaceInviteAcceptView(APIView):
    """Handle direct invite acceptance endpoint.

    Parameters:
    - request: authenticated API request
    - workspace_id: workspace UUID

    Returns:
    - standardized success response with joined workspace data
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceSummaryResponseSerializer

    @extend_schema(operation_id="workspaces_invite_accept")
    def post(self, request, workspace_id):
        workspace = WorkspaceService.accept_invite(user=request.user, workspace_id=workspace_id)
        response_serializer = self.serializer_class(instance=workspace)
        return success_response(
            message="Workspace invite accepted successfully.",
            data={"workspace": response_serializer.data},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Workspaces"])
class WorkspaceInviteTokenAcceptView(APIView):
    """Handle invite acceptance via JWT token endpoint.

    Parameters:
    - request: authenticated API request with token payload

    Returns:
    - standardized success response with joined workspace data
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkspaceInviteTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        workspace = WorkspaceService.accept_invite_via_token(
            user=request.user,
            token=serializer.validated_data["token"],
        )
        return success_response(
            message="Workspace invite token accepted successfully.",
            data={"workspace": workspace},
            status_code=status.HTTP_200_OK,
        )
