"""URLs for the projects app."""

from django.urls import path

from .views import ProjectDetailView, ProjectListView, TagDetailView

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="index"),
    path("tag/<slug:tag_slug>/", TagDetailView.as_view(), name="tag"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="detail"),
]

