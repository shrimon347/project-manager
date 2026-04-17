from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView

from core.responses import success_response
from .serializers import (
    ForgotPasswordSerializer,
    ResendVerificationEmailSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
)
from .services import VerificationService


@extend_schema(tags=["Authentication"])
class VerifyEmailView(APIView):
    """Handle public email verification endpoint."""

    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        """Verify email with token payload."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        VerificationService.verify_email(
            email=serializer.validated_data["email"],
            token=serializer.validated_data["token"],
        )
        return success_response(
            message="Email verified successfully.",
            data={},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Authentication"])
class ResendVerificationEmailView(APIView):
    """Issue a new email verification link for an unverified account."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ResendVerificationEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        sent = VerificationService.try_resend_verification_email(email=email)
        if sent:
            message = "We sent a new verification email. Check your inbox."
        else:
            message = (
                "If an account exists for this address and is not verified yet, "
                "we sent a new confirmation email."
            )
        return success_response(message=message, data={}, status_code=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"])
class ForgotPasswordView(APIView):
    """Handle public forgot-password request endpoint."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        """Issue password reset token for provided email."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        VerificationService.forgot_password(email=serializer.validated_data["email"])
        return success_response(
            message="If the email exists, a reset link has been sent.",
            data={},
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Authentication"])
class ResetPasswordView(APIView):
    """Handle public password reset endpoint."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        """Reset password using email, token, and new password."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        VerificationService.reset_password(
            email=serializer.validated_data["email"],
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["newPassword"],
        )
        return success_response(
            message="Password reset successfully.",
            data={},
            status_code=status.HTTP_200_OK,
        )
