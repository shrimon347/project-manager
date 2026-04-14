from django.conf import settings
from django.db import models

from core.models import BaseModel


class OAuthProvider(models.TextChoices):
    GOOGLE = "google", "Google"
    GITHUB = "github", "GitHub"


class OAuthAccount(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="oauth_accounts")
    provider = models.CharField(max_length=20, choices=OAuthProvider.choices)
    provider_user_id = models.CharField(max_length=255)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "provider_user_id"], name="oauth_provider_user_unique")
        ]
