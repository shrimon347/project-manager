from django.urls import include, path

urlpatterns = [
    path("", include("apps.users.urls")),
    path("", include("apps.verifications.urls")),
    path("", include("apps.workspaces.urls")),
    path("", include("apps.project.urls")),
    path("", include("apps.task.urls")),
    path("", include("apps.comment.urls")),
    path("", include("apps.activity.urls")),
]
