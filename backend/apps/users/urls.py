from django.urls import path

from apps.users import views

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", views.RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("user/profile/", views.ProfileView.as_view(), name="profile"),
    path("user/change-password/", views.ChangePasswordView.as_view(), name="change-password"),
]
