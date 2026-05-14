"""Tests for the about app."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_about_page_returns_200(client):
    response = client.get(reverse("about"))
    assert response.status_code == 200
