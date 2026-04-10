from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.verifications.services import VerificationService
from core.exceptions import ConflictException, ForbiddenException, UnauthorizedException


User = get_user_model()


class AuthService:
    """Application service for authentication workflows.

    Coordinates user registration, login token issuance, and logout token revocation.
    """

    @staticmethod
    def register_user(*, email, name, password):
        """Register a new user and issue an email-verification token.

        Inputs:
        - email: unique user email
        - name: user display name
        - password: plain password

        Outputs:
        - dict with non-sensitive user metadata
        """

        if User.objects.filter(email=email).exists():
            raise ConflictException(detail="User already exists.", errors={"email": "User with this email already exists."})

        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            is_email_verified=False,
        )

        VerificationService.issue_email_verification(user=user)

        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "is_email_verified": user.is_email_verified,
        }

    @staticmethod
    def login_user(*, email, password):
        """Authenticate a verified user and issue JWT pair.

        Inputs:
        - email: user email
        - password: plain password

        Outputs:
        - containing access and refresh tokens
        """

        user = authenticate(email=email, password=password)
        if not user:
            raise UnauthorizedException(detail="Invalid email or password.", code="invalid_credentials")

        if not user.is_active:
            raise ForbiddenException(detail="User account is inactive.", code="inactive_user")

        if not user.is_email_verified:
            VerificationService.ensure_active_email_verification(user=user)
            raise ForbiddenException(
                detail="Email is not verified.",
                code="email_not_verified",
                errors={"email": "Please verify your email before login."},
            )

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def logout_user(*, refresh_token: str) -> None:
        """Revoke refresh token using JWT blacklist and Redis blocklist.

        Inputs:
        - refresh_token: refresh JWT string

        Outputs:
        - None
        """

        try:
            token = RefreshToken(refresh_token)
            jti = str(token.get("jti"))
            exp = int(token.get("exp"))
            ttl_seconds = max(exp - int(timezone.now().timestamp()), 1)

            cache.set(f"jwt:blacklist:{jti}", "1", timeout=ttl_seconds)
            token.blacklist()
        except TokenError as exc:
            raise UnauthorizedException(
                detail="Invalid or expired token.",
                code="invalid_token",
                errors={"refresh": "Invalid or expired token."},
            ) from exc

    @staticmethod
    def refresh_tokens(*, refresh_token):
        """Rotate refresh token and issue new access token.

        Inputs:
        - refresh_token: current refresh JWT

        Outputs:
        - containing new access and refresh tokens
        """

        try:
            old_refresh = RefreshToken(refresh_token)
            user_id = old_refresh.get("user_id")
            user = User.objects.filter(id=user_id).first()
            if not user or not user.is_active:
                raise UnauthorizedException(
                    detail="Invalid user for token.",
                    code="invalid_user",
                    errors={"refresh": "Token user is invalid."},
                )

            new_refresh = RefreshToken.for_user(user)

            old_jti = str(old_refresh.get("jti"))
            old_exp = int(old_refresh.get("exp"))
            ttl_seconds = max(old_exp - int(timezone.now().timestamp()), 1)
            cache.set(f"jwt:blacklist:{old_jti}", "1", timeout=ttl_seconds)
            old_refresh.blacklist()

            return {
                "access": str(new_refresh.access_token),
                "refresh": str(new_refresh),
            }
        except TokenError as exc:
            raise UnauthorizedException(
                detail="Invalid or expired token.",
                code="invalid_token",
                errors={"refresh": "Invalid or expired token."},
            ) from exc

    @staticmethod
    def get_profile(*, user):
        """Return authenticated user profile payload."""

        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "profilePicture": user.avatar_url(),
            "is_email_verified": user.is_email_verified,
        }

    @staticmethod
    def update_profile(*, user, name=None, profile_picture=None):
        """Update authenticated user profile fields."""

        if name is not None:
            user.name = name
        if profile_picture is not None:
            user.avatar = profile_picture
        user.save(update_fields=["name", "avatar", "updated_at"])
        return AuthService.get_profile(user=user)

    @staticmethod
    def change_password(*, user, current_password, new_password):
        """Change authenticated user password after current-password check."""

        if not user.check_password(current_password):
            raise UnauthorizedException(
                detail="Current password is incorrect.",
                code="invalid_current_password",
                errors={"currentPassword": "Current password is incorrect."},
            )
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

