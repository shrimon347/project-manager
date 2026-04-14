from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response
from .serializers import ProfileUpdateSerializer
from .services import UserService


@extend_schema(tags=["Users"])
class ProfileView(APIView):
    """Handle authenticated profile read/update endpoints."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def get(self, request):
        """Return authenticated user profile."""

        profile = UserService.get_profile(user=request.user)
        return success_response(
            message="Profile fetched successfully.",
            data={"profile": profile},
            status_code=status.HTTP_200_OK,
        )

    def put(self, request):
        """Update authenticated user profile fields."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = UserService.update_profile(
            user=request.user,
            name=serializer.validated_data.get("name"),
            profile_picture=serializer.validated_data.get("profilePicture"),
        )
        return success_response(
            message="Profile updated successfully.",
            data={"profile": profile},
            status_code=status.HTTP_200_OK,
        )


