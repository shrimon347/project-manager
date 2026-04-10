from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.responses import success_response
from .responses import (
    clear_refresh_cookie,
    get_refresh_token_from_request,
    set_refresh_cookie,
)
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileUpdateSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)
from .services import AuthService


@extend_schema(tags=["Authentication"])
class RegisterView(APIView):
    """Handle user registration.

    Validates request payload and delegates account creation to service layer.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        """Register a new account and return safe user payload."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.register_user(
            email=serializer.validated_data["email"],
            name=serializer.validated_data["name"],
            password=serializer.validated_data["password"],
        )
        return success_response(
            message="Registration successful. Verify your email.",
            data={"user": result},
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Authentication"])
class LoginView(APIView):
    """Handle user login.

    Validates credentials and delegates token issuance to service layer.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """Authenticate user, return access token, and set refresh cookie."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.login_user(**serializer.validated_data)
        response = success_response(
            message="Login successful.",
            data={
                "token_type": "Bearer",
                "access_token": tokens["access"],
            },
            status_code=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response=response, refresh_token=tokens["refresh"])


@extend_schema(tags=["Authentication"])
class LogoutView(APIView):
    """Handle user logout.

    Accepts refresh token and delegates revocation to service layer.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        """Revoke refresh token and clear refresh cookie."""

        payload = get_refresh_token_from_request(request)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        AuthService.logout_user(refresh_token=serializer.validated_data["refresh"])
        response = success_response(
            message="Logout successful.",
            data={},
            status_code=status.HTTP_200_OK,
        )
        return clear_refresh_cookie(response=response)


@extend_schema(tags=["Authentication"])
class RefreshTokenView(APIView):
    """Handle access token refresh with refresh-token rotation."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        """Rotate refresh token and return a fresh access token."""

        payload = get_refresh_token_from_request(request)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.refresh_tokens(refresh_token=serializer.validated_data["refresh"])
        response = success_response(
            message="Token refreshed successfully.",
            data={
                "token_type": "Bearer",
                "access_token": tokens["access"],
            },
            status_code=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response=response, refresh_token=tokens["refresh"])


@extend_schema(tags=["Authentication"])
class ProfileView(APIView):
    """Handle authenticated profile read/update endpoints."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def get(self, request):
        """Return authenticated user profile."""

        profile = AuthService.get_profile(user=request.user)
        return success_response(
            message="Profile fetched successfully.",
            data={"profile": profile},
            status_code=status.HTTP_200_OK,
        )

    def put(self, request):
        """Update authenticated user profile fields."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = AuthService.update_profile(
            user=request.user,
            name=serializer.validated_data.get("name"),
            profile_picture=serializer.validated_data.get("profilePicture"),
        )
        return success_response(
            message="Profile updated successfully.",
            data={"profile": profile},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Authentication"])
class ChangePasswordView(APIView):
    """Handle authenticated password change endpoint."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        """Change authenticated user's password."""

        serializer = self.serializer_class(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        AuthService.change_password(
            user=request.user,
            current_password=serializer.validated_data["currentPassword"],
            new_password=serializer.validated_data["newPassword"],
        )
        return success_response(
            message="Password changed successfully.",
            data={},
            status_code=status.HTTP_200_OK,
        )
