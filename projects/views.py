"""Views for the projects app."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Project, Tag
from .services import get_adjacent_projects


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


class ProjectListView(ListView):
    model = Project
    paginate_by = 9
    context_object_name = "projects"
    template_name = "projects/index.html"

    selected_tag: Tag | None = None

    def get_queryset(self) -> QuerySet[Project]:
        queryset = Project.objects.published().prefetch_related("tags", "tech_stack")
        tag_slug = self.kwargs.get("tag_slug")

        if tag_slug:
            self.selected_tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags=self.selected_tag).distinct()
        else:
            self.selected_tag = None

        return queryset

    def get_template_names(self) -> list[str]:
        if is_htmx(self.request):
            return ["projects/partials/_project_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["selected_tag"] = self.selected_tag
        context["page_title"] = (
            f"{self.selected_tag.name} projects" if self.selected_tag else "Projects"
        )
        context["meta_description"] = (
            self.selected_tag.description
            if self.selected_tag and self.selected_tag.description
            else "Published Python, Django, HTMX, and hospitality systems projects."
        )
        return context


class TagDetailView(ProjectListView):
    pass


class ProjectDetailView(DetailView):
    model = Project
    context_object_name = "project"
    template_name = "projects/detail.html"

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.published().prefetch_related("tags", "tech_stack")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        previous_project, next_project = get_adjacent_projects(self.object)
        context["previous_project"] = previous_project
        context["next_project"] = next_project
        context["page_title"] = self.object.title
        context["meta_description"] = self.object.summary
        return context

