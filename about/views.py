"""Views for the about app."""

from django.shortcuts import render

from .models import Skill, TimelineEntry


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "about/about.html", {
        "skills": Skill.objects.all(),
        "timeline_entries": TimelineEntry.objects.all(),
    })
