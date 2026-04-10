from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.views import APIView

from .responses import (
    build_login_response,
    build_logout_response,
    build_refresh_response,
    build_register_response,
    get_refresh_token_from_request,
)
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.register_user(
            email=serializer.validated_data["email"],
            name=serializer.validated_data["name"],
            password=serializer.validated_data["password"],
        )
        return build_register_response(user_payload=result)


@extend_schema(tags=["Authentication"])
class LoginView(APIView):
    """Handle user login.

    Validates credentials and delegates token issuance to service layer.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.login_user(**serializer.validated_data)
        return build_login_response(access_token=tokens["access"], refresh_token=tokens["refresh"])


@extend_schema(tags=["Authentication"])
class LogoutView(APIView):
    """Handle user logout.

    Accepts refresh token and delegates revocation to service layer.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        payload = get_refresh_token_from_request(request)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        AuthService.logout_user(refresh_token=serializer.validated_data["refresh"])
        return build_logout_response()


@extend_schema(tags=["Authentication"])
class RefreshTokenView(APIView):
    """Handle access token refresh with refresh-token rotation."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        payload = get_refresh_token_from_request(request)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.refresh_tokens(refresh_token=serializer.validated_data["refresh"])
        return build_refresh_response(access_token=tokens["access"], refresh_token=tokens["refresh"])
