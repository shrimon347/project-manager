from django.urls import path

from apps.workspaces import views

urlpatterns = [
    path("workspaces/", views.WorkspaceCollectionView.as_view(), name="workspace-collection"),
    path("workspaces/<uuid:workspace_id>/", views.WorkspaceDetailView.as_view(), name="workspace-detail"),
    path("workspaces/<uuid:workspace_id>/projects/", views.WorkspaceProjectsView.as_view(), name="workspace-projects"),
    path("workspaces/<uuid:workspace_id>/stats/", views.WorkspaceStatsView.as_view(), name="workspace-stats"),
    path("workspaces/<uuid:workspace_id>/invite-member/", views.WorkspaceInviteView.as_view(), name="workspace-invite-member"),
    path(
        "workspaces/<uuid:workspace_id>/invite/accept/",
        views.WorkspaceInviteAcceptView.as_view(),
        name="workspace-invite-accept",
    ),
    path(
        "workspaces/invite/accept-token/",
        views.WorkspaceInviteTokenAcceptView.as_view(),
        name="workspace-invite-token-accept",
    ),
]
