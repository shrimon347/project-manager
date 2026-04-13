from django.urls import path

from apps.comment import views

urlpatterns = [
    path("comments/task/<uuid:task_id>/", views.CommentByTaskView.as_view(), name="comments-by-task"),
]
