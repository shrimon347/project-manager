from django.urls import path

from apps.auth import views

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/me/", views.MeView.as_view(), name="auth-me"),
    path("auth/refresh/", views.RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("user/change-password/", views.ChangePasswordView.as_view(), name="change-password"),
]
