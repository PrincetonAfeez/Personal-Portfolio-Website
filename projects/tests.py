"""Tests for the projects app."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from .models import Project, Tag, TechStack
from .services import get_adjacent_projects
from .sitemaps import ProjectSitemap

USE_NOW = object()


def make_tag(name: str = "Operations") -> Tag:
    slug = name.lower().replace(" ", "-")
    return Tag.objects.create(name=name, slug=slug)


def make_project(
    title: str,
    *,
    published_at=USE_NOW,
    is_published: bool = True,
    is_featured: bool = False,
    tag: Tag | None = None,
) -> Project:
    project = Project.objects.create(
        title=title,
        summary=f"Summary for {title}",
        body=f"Body for {title}",
        is_published=is_published,
        is_featured=is_featured,
        published_at=timezone.now() if published_at is USE_NOW else published_at,
    )
    if tag:
        project.tags.add(tag)
    return project


@pytest.mark.django_db
def test_published_manager_excludes_unpublished_future_and_empty_dates():
    now = timezone.now()
    published = make_project("Published", published_at=now - timedelta(days=1))
    make_project("Draft", is_published=False, published_at=now - timedelta(days=1))
    make_project("Future", published_at=now + timedelta(days=1))
    make_project("No Date", published_at=None)

    assert list(Project.objects.published()) == [published]


@pytest.mark.django_db
def test_featured_manager_returns_only_featured_published_projects():
    featured = make_project("Featured", is_featured=True)
    make_project("Plain")
    make_project("Draft Featured", is_published=False, is_featured=True)

    assert list(Project.objects.featured()) == [featured]


@pytest.mark.django_db
def test_by_tag_returns_published_projects_for_slug():
    tag = make_tag("Operations")
    other_tag = make_tag("Design")
    matching = make_project("Matching", tag=tag)
    make_project("Other", tag=other_tag)
    make_project("Draft Match", is_published=False, tag=tag)

    assert list(Project.objects.by_tag(tag.slug)) == [matching]


@pytest.mark.django_db
def test_slug_autogeneration_collision_and_manual_slug_preservation():
    first = make_project("Shift Handoff Board")
    second = make_project("Shift Handoff Board")
    manual = Project.objects.create(
        title="Shift Handoff Board",
        slug="custom-handoff",
        summary="Manual summary",
        body="Manual body",
        is_published=True,
        published_at=timezone.now(),
    )

    assert first.slug == "shift-handoff-board"
    assert second.slug == "shift-handoff-board-2"
    assert manual.slug == "custom-handoff"


@pytest.mark.django_db
def test_project_sitemap_includes_only_published_projects(client):
    published = make_project("Sitemap Project")
    unpublished = make_project("Hidden Project", is_published=False)

    response = client.get(reverse("django.contrib.sitemaps.views.sitemap"))

    assert response.status_code == 200
    assert published.get_absolute_url() in response.content.decode()
    assert unpublished.get_absolute_url() not in response.content.decode()


@pytest.mark.django_db
def test_project_sitemap_items_matches_published_queryset():
    published = make_project("Sitemap Item A")
    make_project("Draft Item", is_published=False)
    sm = ProjectSitemap()
    assert list(sm.items()) == list(Project.objects.published())
    assert published in list(sm.items())


@pytest.mark.django_db
def test_project_sitemap_location_and_lastmod():
    project = make_project("Sitemap Loc")
    sm = ProjectSitemap()
    assert sm.location(project) == project.get_absolute_url()
    assert sm.lastmod(project) == project.updated_at


@pytest.mark.django_db
def test_combined_sitemap_xml_includes_static_routes_and_project_loc(client):
    project = make_project("XML Loc Test")
    response = client.get(reverse("django.contrib.sitemaps.views.sitemap"))
    assert response.status_code == 200
    body = response.content.decode()
    assert reverse("home") in body
    assert reverse("projects:index") in body
    assert reverse("about") in body
    assert reverse("contact:index") in body
    assert reverse("resume") in body
    assert project.get_absolute_url() in body


@pytest.mark.django_db
def test_htmx_tag_filter_returns_partial_without_full_layout(client):
    tag = make_tag("Operations")
    make_project("Matching", tag=tag)

    response = client.get(
        reverse("projects:tag", args=[tag.slug]),
        HTTP_HX_REQUEST="true",
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert "project-grid-shell" in content
    assert "<!doctype html>" not in content.lower()
    assert "site-header" not in content


@pytest.mark.django_db
def test_prev_next_logic_respects_published_order():
    now = timezone.now()
    first = make_project("Newest", published_at=now)
    second = make_project("Middle", published_at=now - timedelta(days=1))
    third = make_project("Oldest", published_at=now - timedelta(days=2))
    make_project("Draft", is_published=False, published_at=now + timedelta(days=1))

    first_prev, first_next = get_adjacent_projects(first)
    middle_prev, middle_next = get_adjacent_projects(second)
    last_prev, last_next = get_adjacent_projects(third)

    assert first_prev is None
    assert first_next == second
    assert middle_prev == first
    assert middle_next == third
    assert last_prev == second
    assert last_next is None


@pytest.mark.django_db
def test_unpublished_project_detail_returns_404(client):
    project = make_project("Secret Build", is_published=False)
    response = client.get(project.get_absolute_url())
    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_tag_slug_returns_404(client):
    response = client.get(reverse("projects:tag", args=["no-such-tag"]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_project_list_pagination_second_page(client):
    for i in range(11):
        make_project(f"Bulk Project {i}")
    response = client.get(reverse("projects:index"), {"page": 2})
    assert response.status_code == 200
    assert response.context["page_obj"].number == 2
    assert response.context["page_obj"].paginator.num_pages >= 2


@pytest.mark.django_db
@pytest.mark.parametrize("bad_page", ["0", "99999", "not-a-number"])
def test_project_list_invalid_page_returns_404(client, bad_page):
    make_project("Solo Page")
    response = client.get(reverse("projects:index"), {"page": bad_page})
    assert response.status_code == 404


@pytest.mark.django_db
def test_tag_filter_invalid_page_returns_404(client):
    tag = make_tag("Paged Tag")
    for i in range(11):
        make_project(f"Tagged {i}", tag=tag)
    response = client.get(reverse("projects:tag", args=[tag.slug]), {"page": 99})
    assert response.status_code == 404


@pytest.mark.django_db
def test_adjacent_projects_with_identical_published_at():
    now = timezone.now()
    first = make_project("SameTime A", published_at=now)
    second = make_project("SameTime B", published_at=now)
    third = make_project("SameTime C", published_at=now)

    prev_mid, next_mid = get_adjacent_projects(second)
    assert prev_mid == third
    assert next_mid == first


@pytest.mark.django_db
def test_project_detail_smoke(client):
    tag = make_tag()
    tech = TechStack.objects.create(name="Django", slug="django", category="framework")
    project = make_project("Detail Smoke", tag=tag)
    project.tech_stack.add(tech)

    response = client.get(project.get_absolute_url())

    assert response.status_code == 200
    assert "Detail Smoke" in response.content.decode()
