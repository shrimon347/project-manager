from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.verifications.models import Verification, VerificationType
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

        expires_at = timezone.now() + timedelta(hours=24)
        _, raw_token = Verification.issue_token(
            user=user,
            verification_type=VerificationType.EMAIL_VERIFY,
            expires_at=expires_at,
        )

        AuthService._send_verification_email(email=email, token=raw_token)

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
            AuthService._ensure_active_verification(user=user)
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
    def _send_verification_email(*, email: str, token: str) -> None:
        """Trigger verification email delivery.

        Inputs:
        - email: recipient email
        - token: raw verification token

        Outputs:
        - None
        """

        print(f"[MOCK EMAIL] Send verification token to {email}: {token}")

    @staticmethod
    def _ensure_active_verification(*, user) -> None:
        """Ensure unverified user has a valid email verification token.

        If no active token exists, issue a new one and trigger email delivery.
        A short cooldown avoids spamming repeated login attempts.
        """

        cooldown_key = f"email-verification:cooldown:{user.id}"
        if cache.get(cooldown_key):
            return

        now = timezone.now()
        has_active_token = Verification.objects.filter(
            user=user,
            verification_type=VerificationType.EMAIL_VERIFY,
            is_used=False,
            expires_at__gt=now,
        ).exists()

        if has_active_token:
            return

        expires_at = now + timedelta(hours=24)
        _, raw_token = Verification.issue_token(
            user=user,
            verification_type=VerificationType.EMAIL_VERIFY,
            expires_at=expires_at,
        )
        AuthService._send_verification_email(email=user.email, token=raw_token)
        cache.set(cooldown_key, "1", timeout=60)
