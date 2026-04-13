from django.urls import path

from apps.project import views

urlpatterns = [
    path("projects/<uuid:workspace_id>/create-project", views.ProjectCreateView.as_view(), name="project-create"),
    path("projects/<uuid:project_id>", views.ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<uuid:project_id>/tasks", views.ProjectTasksView.as_view(), name="project-tasks"),
]
