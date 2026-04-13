from django.urls import path

from apps.activity import views

urlpatterns = [
    path("activity/<uuid:resource_id>/", views.ActivityByResourceView.as_view(), name="activity-by-resource"),
]
