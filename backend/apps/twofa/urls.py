from django.urls import path

from apps.twofa.views import TwoFAVerifyView

urlpatterns = [
    path("auth/2fa/verify/", TwoFAVerifyView.as_view(), name="auth-twofa-verify"),
]
