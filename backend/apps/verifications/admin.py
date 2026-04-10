from django.contrib import admin

from .models import Verification


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "verification_type", "is_used", "expires_at", "created_at")
    list_filter = ("verification_type", "is_used")
    search_fields = ("user__email", "token_hash")
