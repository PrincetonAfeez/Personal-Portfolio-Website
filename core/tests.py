"""Tests for the core app."""

import pytest
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone

from projects.models import Project, Tag

from .context_processors import canonical_urls
from .sitemaps import StaticViewSitemap
from .views import handler404, handler500


@override_settings(CANONICAL_URL="https://example.com")
def test_canonical_urls_context_processor():
    request = RequestFactory().get("/projects/", HTTP_HOST="other.test")
    ctx = canonical_urls(request)
    assert ctx["canonical_url"] == "https://example.com/projects/"
    assert ctx["site_origin"] == "https://example.com"


@override_settings(CANONICAL_URL="https://example.com/")
def test_canonical_urls_strips_trailing_slash_on_origin():
    request = RequestFactory().get("/")
    ctx = canonical_urls(request)
    assert ctx["canonical_url"] == "https://example.com/"
    assert ctx["site_origin"] == "https://example.com"


@pytest.mark.django_db
def test_public_url_smoke_tests(client):
    tag = Tag.objects.create(name="Operations", slug="operations")
    project = Project.objects.create(
        title="Smoke Project",
        summary="A published smoke project.",
        body="Project body",
        is_published=True,
        published_at=timezone.now(),
    )
    project.tags.add(tag)

    urls = [
        reverse("home"),
        reverse("projects:index"),
        reverse("projects:tag", args=[tag.slug]),
        reverse("projects:detail", args=[project.slug]),
        reverse("about"),
        reverse("contact:index"),
        reverse("resume"),
        reverse("robots"),
        reverse("django.contrib.sitemaps.views.sitemap"),
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, url


def test_unknown_url_returns_404(client):
    response = client.get("/this-route-should-not-exist-404/")
    assert response.status_code == 404


@override_settings(CANONICAL_URL="https://portfolio.example")
def test_robots_txt_lists_sitemap_under_canonical_host(client):
    response = client.get(reverse("robots"))
    assert response.status_code == 200
    body = response.content.decode()
    assert "Sitemap:" in body
    assert "https://portfolio.example/sitemap.xml" in body


def test_static_view_sitemap_items_and_locations():
    sm = StaticViewSitemap()
    assert sm.items() == [
        "home",
        "projects:index",
        "about",
        "contact:index",
        "resume",
    ]
    for item in sm.items():
        assert sm.location(item) == reverse(item)


def test_handler404_renders_expected_copy():
    request = RequestFactory().get("/missing-page")
    response = handler404(request, Exception("not found"))
    assert response.status_code == 404
    assert "off the floor plan" in response.content.decode()


def test_handler500_renders_expected_copy():
    request = RequestFactory().get("/broken")
    response = handler500(request)
    assert response.status_code == 500
    assert "Something broke" in response.content.decode()

