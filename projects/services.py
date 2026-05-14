"""Services for the projects app."""

from __future__ import annotations

from django.db.models import Q, QuerySet

from .models import Project


def get_featured_projects(limit: int = 3) -> QuerySet[Project]:
    return Project.objects.featured().prefetch_related("tags", "tech_stack")[:limit]


def get_adjacent_projects(project: Project) -> tuple[Project | None, Project | None]:
    newer = Q(published_at__gt=project.published_at) | Q(
        published_at=project.published_at,
        created_at__gt=project.created_at,
    )
    older = Q(published_at__lt=project.published_at) | Q(
        published_at=project.published_at,
        created_at__lt=project.created_at,
    )
    base = Project.objects.published()
    previous_project = (
        base.filter(newer).order_by("published_at", "created_at").only("id", "title", "slug").first()
    )
    next_project = (
        base.filter(older)
        .order_by("-published_at", "-created_at")
        .only("id", "title", "slug")
        .first()
    )
    return previous_project, next_project
