import json
import re
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction

from apps.auth.services import AuthService
from apps.oauth.models import OAuthAccount, OAuthProvider
from apps.twofa.services import TwoFAService
from core.exceptions import ConflictException, UnauthorizedException

User = get_user_model()


class OAuthService:
    """Application service for OAuth login and account linking.

    Validates provider tokens, resolves the owning user account, links OAuth identities,
    updates user profile information, and returns either 2FA challenge data or JWT tokens.
    """

    @staticmethod
    def login_with_provider(*, provider: str, token: str):
        """Authenticate a user via OAuth provider token.

        Args:
            provider: OAuth provider key ("google" or "github").
            token: Provider-issued token from the client.

        Returns:
            dict: Either JWT payload (`access`, `refresh`) or 2FA challenge payload.
        """

        profile = OAuthService._verify_provider_token(provider=provider, token=token)
        user = OAuthService._resolve_or_create_user(provider=provider, profile=profile)
        OAuthService._update_user_profile(user=user, profile=profile, provider=provider)

        if user.is_2fa_enabled:
            return TwoFAService.start_twofa_challenge(user=user)
        return AuthService.issue_jwt_for_user(user=user)

    @staticmethod
    def _verify_provider_token(*, provider: str, token: str) -> dict:
        if provider == OAuthProvider.GOOGLE:
            return OAuthService._verify_google_token(token=token)
        if provider == OAuthProvider.GITHUB:
            return OAuthService._verify_github_token(token=token)
        raise UnauthorizedException(detail="Unsupported OAuth provider.", code="unsupported_provider")

    @staticmethod
    def _verify_google_token(*, token: str) -> dict:
        query = urllib.parse.urlencode({"id_token": token})
        url = f"https://oauth2.googleapis.com/tokeninfo?{query}"
        payload = OAuthService._fetch_json(url=url, headers={})
        email = (payload.get("email") or "").strip().lower()
        provider_user_id = str(payload.get("sub") or "").strip()
        if not email or not provider_user_id:
            raise UnauthorizedException(
                detail="Invalid Google token payload.",
                code="invalid_oauth_token",
            )
        return {
            "provider_user_id": provider_user_id,
            "email": email,
            "name": (payload.get("name") or "").strip(),
            "avatar_url": payload.get("picture") or "",
            "extra_data": payload,
        }

    @staticmethod
    def _verify_github_token(*, token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "project-manager-api",
        }
        user_payload = OAuthService._fetch_json(url="https://api.github.com/user", headers=headers)
        emails_payload = OAuthService._fetch_json(url="https://api.github.com/user/emails", headers=headers)

        provider_user_id = str(user_payload.get("id") or "").strip()
        email = OAuthService._extract_github_email(emails=emails_payload, fallback=user_payload.get("email"))
        if not email:
            raise ConflictException(
                detail="GitHub account email is required.",
                code="oauth_email_missing",
                errors={"email": "Public or primary email is required in GitHub account."},
            )
        if not provider_user_id:
            raise UnauthorizedException(
                detail="Invalid GitHub token payload.",
                code="invalid_oauth_token",
            )
        return {
            "provider_user_id": provider_user_id,
            "email": email,
            "name": (user_payload.get("name") or user_payload.get("login") or "").strip(),
            "avatar_url": user_payload.get("avatar_url") or "",
            "extra_data": {
                "user": user_payload,
                "emails": emails_payload,
            },
        }

    @staticmethod
    def _extract_github_email(*, emails, fallback):
        if isinstance(fallback, str) and fallback.strip():
            return fallback.strip().lower()
        if isinstance(emails, list):
            primary_verified = next(
                (item for item in emails if item.get("primary") and item.get("verified") and item.get("email")),
                None,
            )
            if primary_verified:
                return primary_verified["email"].strip().lower()
            any_verified = next((item for item in emails if item.get("verified") and item.get("email")), None)
            if any_verified:
                return any_verified["email"].strip().lower()
        return ""

    @staticmethod
    @transaction.atomic
    def _resolve_or_create_user(*, provider: str, profile: dict):
        oauth_account = OAuthAccount.objects.select_related("user").filter(
            provider=provider,
            provider_user_id=profile["provider_user_id"],
        ).first()
        if oauth_account:
            oauth_account.extra_data = profile["extra_data"]
            oauth_account.save(update_fields=["extra_data", "updated_at"])
            return oauth_account.user

        user = User.objects.filter(email=profile["email"]).first()
        if not user:
            user = User.objects.create_user(
                email=profile["email"],
                name=profile["name"] or profile["email"].split("@")[0],
                password=User.objects.make_random_password(),
                is_email_verified=True,
            )

        OAuthAccount.objects.get_or_create(
            provider=provider,
            provider_user_id=profile["provider_user_id"],
            defaults={
                "user": user,
                "extra_data": profile["extra_data"],
            },
        )
        return user

    @staticmethod
    def _update_user_profile(*, user, profile: dict, provider: str) -> None:
        update_fields = ["updated_at"]
        if profile["name"] and user.name != profile["name"]:
            user.name = profile["name"]
            update_fields.append("name")
        if not user.is_email_verified:
            user.is_email_verified = True
            update_fields.append("is_email_verified")

        avatar_file = OAuthService._download_avatar_content(
            url=profile.get("avatar_url") or "",
            provider=provider,
            provider_user_id=profile["provider_user_id"],
        )
        if avatar_file:
            filename, content = avatar_file
            user.avatar.save(filename, content, save=False)
            update_fields.append("avatar")

        if len(update_fields) > 1:
            user.save(update_fields=list(dict.fromkeys(update_fields)))

    @staticmethod
    def _download_avatar_content(*, url: str, provider: str, provider_user_id: str):
        if not url:
            return None
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "project-manager-api"})
            with urllib.request.urlopen(request, timeout=5) as response:
                content = response.read()
                content_type = response.headers.get("Content-Type", "")
        except (urllib.error.URLError, ValueError):
            return None

        if not content:
            return None
        ext = OAuthService._image_extension(content_type=content_type, url=url)
        return (f"oauth-{provider}-{provider_user_id}-{uuid4().hex}.{ext}", ContentFile(content))

    @staticmethod
    def _image_extension(*, content_type: str, url: str) -> str:
        content_map = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }
        normalized = (content_type or "").lower().split(";")[0].strip()
        if normalized in content_map:
            return content_map[normalized]

        parsed = urllib.parse.urlparse(url)
        match = re.search(r"\.(jpg|jpeg|png|webp|gif)$", parsed.path.lower())
        if match:
            ext = match.group(1)
            return "jpg" if ext == "jpeg" else ext
        return "jpg"

    @staticmethod
    def _fetch_json(*, url: str, headers: dict):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except (urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
            raise UnauthorizedException(
                detail="OAuth token validation failed.",
                code="oauth_validation_failed",
            ) from exc
