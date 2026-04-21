from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from apps.twofa.services import TwoFAService
from apps.verifications.services import VerificationService
from core.exceptions import ConflictException, ForbiddenException, UnauthorizedException

User = get_user_model()


class AuthService:
    """Application service for authentication workflows."""

    @staticmethod
    def register_user(*, email, name, password):
        """Register a new user and issue an email verification token."""

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
        """Authenticate user and continue to 2FA or token issuance."""

        AuthService._enforce_login_rate_limit(email=email)
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

        AuthService._clear_login_rate_limit(email=email)
        if user.is_2fa_enabled:
            return TwoFAService.start_twofa_challenge(user=user)
        return AuthService.issue_jwt_for_user(user=user)

    @staticmethod
    def get_current_user(*, user):
        """Return the authenticated user for read-only profile endpoints."""

        return user

    @staticmethod
    def issue_jwt_for_user(*, user):
        """Issue access and refresh JWT tokens for an authenticated user."""

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }

    @staticmethod
    def logout_user(*, refresh_token: str) -> None:
        """Revoke refresh token via blacklist and Redis."""

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
        """Rotate refresh token and issue new access token."""
        # print("🔍 validating refresh token...")
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
            # print("❌ TokenError:", str(exc))
            raise UnauthorizedException(
                detail="Invalid or expired token.",
                code="invalid_token",
                errors={"refresh": "Invalid or expired token."},
            ) from exc

    @staticmethod
    def change_password(*, user, current_password, new_password):
        """Change authenticated user password after validation."""

        if not user.check_password(current_password):
            raise UnauthorizedException(
                detail="Current password is incorrect.",
                code="invalid_current_password",
                errors={"currentPassword": "Current password is incorrect."},
            )
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

    @staticmethod
    def _enforce_login_rate_limit(*, email):
        key = f"auth:login:attempts:{email}"
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, timeout=60)
        if attempts > 10:
            raise ForbiddenException(
                detail="Too many login attempts. Please try again later.",
                code="too_many_login_attempts",
            )

    @staticmethod
    def _clear_login_rate_limit(*, email):
        cache.delete(f"auth:login:attempts:{email}")
