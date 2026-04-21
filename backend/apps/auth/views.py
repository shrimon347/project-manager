from core.responses import success_response
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.auth.responses import (
    clear_refresh_cookie,
    get_refresh_token_from_request,
    set_refresh_cookie,
)
from apps.auth.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    MeSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)
from apps.auth.services import AuthService


@extend_schema(tags=["Authentication"])
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
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
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.login_user(**serializer.validated_data)
        if tokens.get("requires_2fa"):
            return success_response(
                message="Two-factor authentication required.",
                data={
                    "requires_2fa": True,
                    "temp_token": tokens["temp_token"],
                },
                status_code=status.HTTP_200_OK,
            )
        user = tokens["user"]
        response = success_response(
            message="Login successful.",
            data={
                "access": tokens["access"],
                "user": MeSerializer(user).data,
            },
            status_code=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response=response, refresh_token=tokens["refresh"])


@extend_schema(tags=["Authentication"])
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        payload = get_refresh_token_from_request(request)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        AuthService.logout_user(refresh_token=serializer.validated_data["refresh"])
        response = success_response(
            message="Logout successful.", data={}, status_code=status.HTTP_200_OK
        )
        return clear_refresh_cookie(response=response)


@extend_schema(tags=["Authentication"])
class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        payload = get_refresh_token_from_request(request)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.refresh_tokens(
            refresh_token=serializer.validated_data["refresh"]
        )
        response = success_response(
            message="Token refreshed successfully.",
            data={
                "access": tokens["access"],
            },
            status_code=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response=response, refresh_token=tokens["refresh"])


@extend_schema(tags=["Authentication"])
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )
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


@extend_schema(tags=["Authentication"])
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = AuthService.get_current_user(user=request.user)
        return success_response(
            message="Current user retrieved successfully.",
            data=MeSerializer(user).data,
            status_code=status.HTTP_200_OK,
        )
