from django.urls import path

from apps.users import views

urlpatterns = [
    path("user/profile/", views.ProfileView.as_view(), name="profile"),
]
