class UserService:
    """Application service for user profile operations."""

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
        return UserService.get_profile(user=user)

