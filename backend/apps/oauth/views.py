from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.auth.responses import set_refresh_cookie
from apps.auth.serializers import MeSerializer
from apps.oauth.serializers import OAuthLoginSerializer
from apps.oauth.services import OAuthService
from core.responses import success_response


@extend_schema(tags=["Authentication"])
class OAuthLoginView(APIView):
    """Handle OAuth login for Google and GitHub providers.

    Validates provider payload, delegates OAuth authentication flow to service layer,
    and returns either a 2FA challenge or authenticated JWT response.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = OAuthLoginSerializer

    def post(self, request):
        """Authenticate user with provider token and complete login flow.

        Parameters:
            request: DRF request containing `provider` and `token`.

        Returns:
            Response: Standardized success payload with 2FA challenge or JWT access token.
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = OAuthService.login_with_provider(
            provider=serializer.validated_data["provider"],
            token=serializer.validated_data["token"],
        )
        if result.get("requires_2fa"):
            return success_response(
                message="Two-factor authentication required.",
                data={
                    "requires_2fa": True,
                    "temp_token": result["temp_token"],
                },
                status_code=status.HTTP_200_OK,
            )

        user = result["user"]
        response = success_response(
            message="Login successful.",
            data={
                "access": result["access"],
                "user": MeSerializer(user).data,
            },
            status_code=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response=response, refresh_token=result["refresh"])
