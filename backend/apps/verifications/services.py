from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from apps.verifications.models import Verification, VerificationType
from core.exceptions import ConflictException, CustomAPIException, UnauthorizedException

User = get_user_model()


class VerificationService:
    """Service layer for verification and password-recovery flows."""

    @staticmethod
    def verify_email(*, email, token):
        """Verify a user's email by validating and consuming token."""

        user = User.objects.filter(email=email).first()
        if not user:
            raise UnauthorizedException(
                detail="Invalid verification request.",
                code="invalid_verification_request",
                errors={"email": "Invalid email or token."},
            )

        record = VerificationService._validate_active_verification(
            user=user,
            raw_token=token,
            verification_type=VerificationType.EMAIL_VERIFY,
        )
        record.is_used = True
        record.used_at = timezone.now()
        record.save(update_fields=["is_used", "used_at", "updated_at"])

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified", "updated_at"])

    @staticmethod
    def forgot_password(*, email):
        """Issue a password-reset token for an existing account."""

        user = User.objects.filter(email=email).first()
        if not user:
            return

        expires_at = timezone.now() + timedelta(minutes=30)
        _, raw_token = Verification.issue_token(
            user=user,
            verification_type=VerificationType.PASSWORD_RESET,
            expires_at=expires_at,
        )
        VerificationService._send_password_reset_email(email=email, token=raw_token)

    @staticmethod
    def reset_password(*, email, token, new_password):
        """Reset account password after validating reset token."""

        user = User.objects.filter(email=email).first()
        if not user:
            raise UnauthorizedException(
                detail="Invalid reset request.",
                code="invalid_reset_request",
                errors={"email": "Invalid email or token."},
            )

        record = VerificationService._validate_active_verification(
            user=user,
            raw_token=token,
            verification_type=VerificationType.PASSWORD_RESET,
        )
        record.is_used = True
        record.used_at = timezone.now()
        record.save(update_fields=["is_used", "used_at", "updated_at"])

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

    @staticmethod
    def issue_email_verification(*, user, expires_in_hours=24):
        """Create email-verification token and dispatch email."""

        expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        _, raw_token = Verification.issue_token(
            user=user,
            verification_type=VerificationType.EMAIL_VERIFY,
            expires_at=expires_at,
        )
        VerificationService._send_verification_email(email=user.email, token=raw_token)

    @staticmethod
    def ensure_active_email_verification(*, user):
        """Ensure there is a valid active email verification token."""

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

        VerificationService.issue_email_verification(user=user)
        cache.set(cooldown_key, "1", timeout=60)

    @staticmethod
    def try_resend_verification_email(*, email: str) -> bool:
        """Send a fresh verification email if the user exists and is unverified.

        Returns True if an email was sent, False if no user exists (generic response in view).
        Raises ConflictException if the address is already verified.
        Raises CustomAPIException if resend is rate-limited.
        """

        user = User.objects.filter(email=email).first()
        if not user:
            return False
        if user.is_email_verified:
            raise ConflictException(
                detail="This email is already verified.",
                code="already_verified",
                errors={"email": "You can sign in with this address."},
            )
        cooldown_key = f"email-verification:resend:{user.id}"
        if cache.get(cooldown_key):
            raise CustomAPIException(
                detail="Please wait before requesting another verification email.",
                code="resend_cooldown",
                errors={"email": "Try again in a minute."},
            )
        cache.set(cooldown_key, "1", timeout=60)
        VerificationService.issue_email_verification(user=user)
        return True

    @staticmethod
    def _send_verification_email(*, email, token):
        """Dispatch verification email via provider hook."""

        query = urlencode({"email": email, "token": token})
        verify_url = f"{settings.FRONTEND_URL}/verify-email?{query}"
        print(f"[MOCK EMAIL] Send verification to {email}\n  Link: {verify_url}")

    @staticmethod
    def _send_password_reset_email(*, email, token):
        """Dispatch password-reset email via provider hook."""

        print(f"[MOCK EMAIL] Send password reset token to {email}: {token}")

    @staticmethod
    def send_twofa_otp_email(*, email, otp, expires_in_minutes=5):
        """Dispatch two-factor OTP email via provider hook."""

        print(
            f"[MOCK EMAIL] Send 2FA OTP to {email}: {otp} (expires in {expires_in_minutes} minutes)"
        )

    @staticmethod
    def _validate_active_verification(*, user, raw_token, verification_type):
        """Validate token hash, active state, and expiry for a user."""

        token_hash = Verification.hash_token(raw_token)
        verification = (
            Verification.objects.filter(
                user=user,
                verification_type=verification_type,
                token_hash=token_hash,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not verification:
            raise UnauthorizedException(
                detail="Invalid verification token.",
                code="invalid_token",
                errors={"token": "Invalid token."},
            )
        if verification.is_expired():
            raise CustomAPIException(
                detail="Verification token expired.",
                code="token_expired",
                errors={"token": "Token has expired."},
            )
        return verification
