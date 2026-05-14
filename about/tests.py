"""Tests for the about app."""

from datetime import date

import pytest
from django.urls import reverse

from .models import Skill, TimelineEntry


@pytest.mark.django_db
def test_about_page_returns_200(client):
    response = client.get(reverse("about"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_skill_queryset_ordering_matches_meta():
    """Meta.ordering: category ASC, proficiency DESC, name ASC."""
    Skill.objects.create(name="X", category="Zeta", proficiency=1)
    Skill.objects.create(name="B", category="Alpha", proficiency=5)
    Skill.objects.create(name="A", category="Alpha", proficiency=5)
    Skill.objects.create(name="M", category="Alpha", proficiency=3)
    assert list(Skill.objects.values_list("name", flat=True)) == ["A", "B", "M", "X"]


@pytest.mark.django_db
def test_timeline_queryset_ordering_newest_first():
    """Meta.ordering: -date (newest first)."""
    TimelineEntry.objects.create(
        date=date(2020, 1, 1),
        title="Old",
        description="Earlier milestone.",
        entry_type=TimelineEntry.EntryType.WORK,
    )
    TimelineEntry.objects.create(
        date=date(2024, 6, 1),
        title="New",
        description="Recent milestone.",
        entry_type=TimelineEntry.EntryType.LEARNING,
    )
    assert list(TimelineEntry.objects.values_list("title", flat=True)) == ["New", "Old"]
