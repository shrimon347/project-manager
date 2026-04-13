from django.urls import path

from apps.task import views

urlpatterns = [
    path("tasks/<uuid:project_id>/create-task", views.TaskCreateView.as_view(), name="task-create"),
    path("tasks/my-tasks", views.TaskMyTasksView.as_view(), name="task-my-tasks"),
    path("tasks/<uuid:task_id>", views.TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<uuid:task_id>/add-subtask", views.TaskSubTaskCreateView.as_view(), name="task-add-subtask"),
    path("tasks/<uuid:task_id>/add-comment", views.TaskCommentCreateView.as_view(), name="task-add-comment"),
    path("tasks/<uuid:task_id>/watch", views.TaskWatchToggleView.as_view(), name="task-watch-toggle"),
    path("tasks/<uuid:task_id>/achieved", views.TaskAchievedToggleView.as_view(), name="task-achieved-toggle"),
    path(
        "tasks/<uuid:task_id>/update-subtask/<uuid:subtask_id>",
        views.TaskSubTaskUpdateView.as_view(),
        name="task-update-subtask",
    ),
    path("tasks/<uuid:task_id>/title", views.TaskTitleUpdateView.as_view(), name="task-update-title"),
    path("tasks/<uuid:task_id>/description", views.TaskDescriptionUpdateView.as_view(), name="task-update-description"),
    path("tasks/<uuid:task_id>/status", views.TaskStatusUpdateView.as_view(), name="task-update-status"),
    path("tasks/<uuid:task_id>/assignees", views.TaskAssigneesUpdateView.as_view(), name="task-update-assignees"),
    path("tasks/<uuid:task_id>/priority", views.TaskPriorityUpdateView.as_view(), name="task-update-priority"),
    path("tasks/<uuid:task_id>/activity", views.TaskActivityView.as_view(), name="task-activity"),
    path("tasks/<uuid:task_id>/comments", views.TaskCommentsView.as_view(), name="task-comments"),
]
