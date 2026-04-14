from django.urls import path

from apps.oauth.views import OAuthLoginView

urlpatterns = [
    path("auth/oauth/login/", OAuthLoginView.as_view(), name="auth-oauth-login"),
]
