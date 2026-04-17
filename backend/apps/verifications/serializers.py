from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class VerifyEmailSerializer(serializers.Serializer):
    """Validate verify-email payload.

    Inputs:
    - email: account email address
    - token: email verification token

    Outputs:
    - normalized email and token in validated_data
    """

    email = serializers.EmailField()
    token = serializers.CharField()

    def validate_email(self, value):
        return value.strip().lower()


class ResendVerificationEmailSerializer(serializers.Serializer):
    """Request another email verification link (same shape as forgot-password email)."""

    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class ForgotPasswordSerializer(serializers.Serializer):
    """Validate forgot-password payload.

    Inputs:
    - email: account email address

    Outputs:
    - normalized email in validated_data
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    """Validate reset-password payload.

    Inputs:
    - email: account email address
    - token: password reset token
    - newPassword: new password candidate
    - confirmPassword: confirmation password

    Outputs:
    - normalized/reset-ready payload in validated_data
    """

    email = serializers.EmailField()
    token = serializers.CharField()
    newPassword = serializers.CharField(write_only=True, trim_whitespace=False)
    confirmPassword = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        if attrs["newPassword"] != attrs["confirmPassword"]:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})
        validate_password(attrs["newPassword"])
        return attrs
