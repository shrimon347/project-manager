from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.auth.responses import set_refresh_cookie
from apps.auth.serializers import MeSerializer
from apps.twofa.serializers import TwoFAVerifySerializer
from apps.twofa.services import TwoFAService
from core.responses import success_response


@extend_schema(tags=["Authentication"])
class TwoFAVerifyView(APIView):
    """Handle two-factor authentication OTP verification endpoint.

    Validates submitted OTP and temporary token, then delegates verification
    and final JWT issuance to the service layer.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = TwoFAVerifySerializer

    def post(self, request):
        """Verify OTP challenge and return authenticated JWT response.

        Parameters:
            request: DRF request containing `otp` and `temp_token`.

        Returns:
            Response: Standardized success payload with access token and refresh cookie.
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = TwoFAService.verify_twofa(
            temp_token=serializer.validated_data["temp_token"],
            otp=serializer.validated_data["otp"],
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
