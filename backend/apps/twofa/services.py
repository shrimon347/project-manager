import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, TokenError

from apps.verifications.services import VerificationService
from core.exceptions import ForbiddenException, UnauthorizedException

User = get_user_model()


class TwoFAService:
    """Application service for two-factor authentication challenges.

    Generates OTP challenges, stores OTPs in Redis with expiry, validates challenge
    submissions, and finalizes login by issuing regular JWT tokens.
    """

    OTP_TTL_SECONDS = 300
    TEMP_TOKEN_TTL_SECONDS = 300
    LOGIN_ATTEMPT_WINDOW_SECONDS = 60
    LOGIN_ATTEMPT_LIMIT = 8

    @staticmethod
    def start_twofa_challenge(*, user):
        """Start 2FA challenge for an authenticated first factor.

        Args:
            user: User who passed the primary authentication factor.

        Returns:
            dict: Challenge payload with `requires_2fa` and short-lived `temp_token`.
        """

        otp_code = TwoFAService._generate_otp()
        cache.set(TwoFAService._otp_key(user_id=user.id), otp_code, timeout=TwoFAService.OTP_TTL_SECONDS)

        user.two_fa_otp = otp_code
        user.two_fa_otp_expires = timezone.now() + timedelta(seconds=TwoFAService.OTP_TTL_SECONDS)
        user.save(update_fields=["two_fa_otp", "two_fa_otp_expires", "updated_at"])
        VerificationService.send_twofa_otp_email(email=user.email, otp=otp_code, expires_in_minutes=5)

        temp_token = AccessToken.for_user(user)
        temp_token.set_exp(lifetime=timedelta(seconds=TwoFAService.TEMP_TOKEN_TTL_SECONDS))
        temp_token["purpose"] = "2fa_login"
        return {
            "requires_2fa": True,
            "temp_token": str(temp_token),
        }

    @staticmethod
    def verify_twofa(*, temp_token: str, otp: str):
        """Verify OTP for a pending 2FA challenge and issue JWT tokens.

        Args:
            temp_token: Short-lived JWT proving successful primary authentication.
            otp: Six-digit one-time password submitted by the user.

        Returns:
            dict: Standard authenticated JWT payload with `access` and `refresh`.
        """

        user = TwoFAService._user_from_temp_token(temp_token=temp_token)
        TwoFAService._enforce_verify_rate_limit(user_id=user.id)

        cached_otp = cache.get(TwoFAService._otp_key(user_id=user.id))
        if not cached_otp or str(cached_otp) != str(otp):
            raise UnauthorizedException(
                detail="Invalid or expired OTP.",
                code="invalid_otp",
                errors={"otp": "Invalid or expired OTP."},
            )

        cache.delete(TwoFAService._otp_key(user_id=user.id))
        user.two_fa_otp = None
        user.two_fa_otp_expires = None
        user.save(update_fields=["two_fa_otp", "two_fa_otp_expires", "updated_at"])
        cache.delete(TwoFAService._attempts_key(user_id=user.id))

        from apps.auth.services import AuthService

        return AuthService.issue_jwt_for_user(user=user)

    @staticmethod
    def _user_from_temp_token(*, temp_token: str):
        try:
            token = AccessToken(temp_token)
            if token.get("purpose") != "2fa_login":
                raise UnauthorizedException(
                    detail="Invalid temporary token.",
                    code="invalid_temp_token",
                    errors={"temp_token": "Invalid temporary token."},
                )
            user_id = token.get("user_id")
        except TokenError as exc:
            raise UnauthorizedException(
                detail="Temporary token expired or invalid.",
                code="invalid_temp_token",
                errors={"temp_token": "Temporary token expired or invalid."},
            ) from exc

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            raise UnauthorizedException(
                detail="Invalid user for temporary token.",
                code="invalid_temp_token_user",
                errors={"temp_token": "Invalid user for temporary token."},
            )
        if not user.is_2fa_enabled:
            raise ForbiddenException(
                detail="Two-factor authentication is not enabled for this user.",
                code="twofa_not_enabled",
            )
        return user

    @staticmethod
    def _enforce_verify_rate_limit(*, user_id):
        key = TwoFAService._attempts_key(user_id=user_id)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, timeout=TwoFAService.LOGIN_ATTEMPT_WINDOW_SECONDS)
        if attempts > TwoFAService.LOGIN_ATTEMPT_LIMIT:
            raise ForbiddenException(
                detail="Too many OTP attempts. Please try again later.",
                code="too_many_otp_attempts",
            )

    @staticmethod
    def _generate_otp():
        return f"{secrets.randbelow(1000000):06d}"

    @staticmethod
    def _otp_key(*, user_id):
        return f"otp_{user_id}"

    @staticmethod
    def _attempts_key(*, user_id):
        return f"otp_attempts_{user_id}"
