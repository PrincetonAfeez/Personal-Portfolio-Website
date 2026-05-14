"""Views for the core app."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse

from about.models import Skill, TimelineEntry
from projects.models import Tag
from projects.services import get_featured_projects


def home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "core/home.html",
        {
            "featured_projects": get_featured_projects(),
            "tags": Tag.objects.all()[:8],
            "page_title": "Hospitality tech portfolio",
            "meta_description": settings.SITE_TAGLINE,
        },
    )


def about(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "about/about.html",
        {
            "skills": Skill.objects.all(),
            "timeline_entries": TimelineEntry.objects.all(),
            "page_title": "About",
            "meta_description": "A hospitality professional learning Python, Django, HTMX, and systems architecture.",
        },
    )


def resume(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "core/resume.html",
        {
            "page_title": "Resume",
            "meta_description": "Resume for hospitality operations and hospitality technology roles.",
        },
    )


def robots_txt(request: HttpRequest) -> HttpResponse:
    response = TemplateResponse(request, "core/robots.txt", {"canonical_url": settings.CANONICAL_URL})
    response["Content-Type"] = "text/plain"
    return response


def handler404(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    return render(request, "500.html", status=500)

