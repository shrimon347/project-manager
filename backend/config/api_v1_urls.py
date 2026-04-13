from django.urls import include, path

urlpatterns = [
    path("", include("apps.users.urls")),
    path("", include("apps.verifications.urls")),
    path("", include("apps.workspaces.urls")),
]
