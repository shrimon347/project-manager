from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Validate registration payload.

    Inputs:
    - email: unique email address
    - name: display name
    - password: account password
    - confirm_password: repeated password

    Outputs:
    - validated_data with normalized fields for service usage
    """

    email = serializers.EmailField()
    name = serializers.CharField(max_length=50)
    password = serializers.CharField(
        write_only=True, min_length=8, trim_whitespace=False
    )
    confirm_password = serializers.CharField(
        write_only=True, min_length=8, trim_whitespace=False
    )

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return normalized

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    """Validate login payload.

    Inputs:
    - email: user email
    - password: plain password

    Outputs:
    - validated_data with normalized credentials
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        return value.strip().lower()


class LogoutSerializer(serializers.Serializer):
    """Validate logout payload.

    Inputs:
    - refresh: refresh JWT token

    Outputs:
    - validated_data containing refresh token string
    """

    refresh = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    """Validate refresh payload.

    Inputs:
    - refresh: refresh JWT token

    Outputs:
    - validated_data containing refresh token string
    """

    refresh = serializers.CharField()


class ProfileUpdateSerializer(serializers.Serializer):
    """Validate profile update payload.

    Inputs:
    - name: optional display name
    - profilePicture: optional avatar image

    Outputs:
    - validated_data with profile fields to update
    """

    name = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    profilePicture = serializers.ImageField(required=False, allow_null=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Validate change-password payload.

    Inputs:
    - currentPassword: current account password
    - newPassword: new password candidate
    - confirmPassword: confirmation password

    Outputs:
    - validated_data with password update fields
    """

    currentPassword = serializers.CharField(write_only=True, trim_whitespace=False)
    newPassword = serializers.CharField(write_only=True, trim_whitespace=False)
    confirmPassword = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs["newPassword"] != attrs["confirmPassword"]:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})

        user = self.context.get("user")
        validate_password(attrs["newPassword"], user=user)
        return attrs


