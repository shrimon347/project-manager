from django.urls import path

from apps.verifications import views

# Verification-domain endpoints are isolated under this app
# to keep recovery/verification flows modular as the project grows.
urlpatterns = [
    path("auth/verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("auth/forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
]
