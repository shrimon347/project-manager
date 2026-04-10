import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class VerificationType(models.TextChoices):
    EMAIL_VERIFY = "email_verify", "Email Verify"
    PASSWORD_RESET = "password_reset", "Password Reset"
    TWO_FA = "two_fa", "Two Factor Auth"


class Verification(BaseModel):
    """Token lifecycle model for verification and recovery flows."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="verifications")
    verification_type = models.CharField(max_length=32, choices=VerificationType.choices)
    token_hash = models.CharField(max_length=64, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["user", "verification_type", "is_used"]),
            models.Index(fields=["verification_type", "expires_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "verification_type", "token_hash"],
                name="uniq_user_verification_type_token_hash",
            )
        ]

    def __str__(self):
        return f"{self.verification_type} for {self.user_id}"

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def issue_token(cls, user, verification_type: str, expires_at):
        """Create and return (instance, raw_token). Store only hash in DB."""
        raw_token = secrets.token_urlsafe(32)
        token_hash = cls.hash_token(raw_token)
        instance = cls.objects.create(
            user=user,
            verification_type=verification_type,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        return instance, raw_token

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
