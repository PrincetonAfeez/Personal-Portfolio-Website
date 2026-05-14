"""Tests for the contact app."""

import pytest
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from .models import ContactSubmission
from .views import client_ip


def _contact_payload(**extra):
    return {
        "name": "Alex Manager",
        "email": "alex@example.com",
        "message": "Can we talk about a service operations tool?",
        "referral_source": "",
        **extra,
    }


@pytest.mark.django_db
def test_contact_form_valid_submission_saves(client):
    cache.clear()
    response = client.post(
        reverse("contact:index"),
        _contact_payload(),
        HTTP_HX_REQUEST="true",
        REMOTE_ADDR="127.0.0.1",
    )

    assert response.status_code == 200
    assert ContactSubmission.objects.count() == 1
    assert "Message received" in response.content.decode()


@pytest.mark.django_db
def test_contact_stores_remote_addr_when_forwarded_header_untrusted(client):
    cache.clear()
    client.post(
        reverse("contact:index"),
        _contact_payload(),
        HTTP_HX_REQUEST="true",
        HTTP_X_FORWARDED_FOR="203.0.113.99",
        REMOTE_ADDR="198.51.100.22",
    )
    row = ContactSubmission.objects.get()
    assert row.ip_address == "198.51.100.22"


@pytest.mark.django_db
def test_contact_form_invalid_submission_shows_errors(client):
    cache.clear()
    response = client.post(
        reverse("contact:index"),
        {"name": "", "email": "bad-email", "message": "", "referral_source": ""},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert ContactSubmission.objects.count() == 0
    assert "Enter a valid email address" in response.content.decode()


@pytest.mark.django_db
def test_contact_honeypot_filled_does_not_save(client):
    cache.clear()
    response = client.post(
        reverse("contact:index"),
        _contact_payload(referral_source="https://spam.example"),
        HTTP_HX_REQUEST="true",
        REMOTE_ADDR="127.0.0.1",
    )
    assert response.status_code == 200
    assert ContactSubmission.objects.count() == 0
    assert "Message received" in response.content.decode()


@pytest.mark.django_db
def test_contact_rate_limit_blocks_after_max(client, settings):
    cache.clear()
    settings.CONTACT_RATE_LIMIT_MAX = 2
    settings.CONTACT_RATE_LIMIT_WINDOW = 600
    url = reverse("contact:index")
    for _ in range(2):
        response = client.post(
            url,
            _contact_payload(),
            HTTP_HX_REQUEST="true",
            REMOTE_ADDR="198.51.100.9",
        )
        assert response.status_code == 200
    assert ContactSubmission.objects.count() == 2
    response = client.post(
        url,
        _contact_payload(),
        HTTP_HX_REQUEST="true",
        REMOTE_ADDR="198.51.100.9",
    )
    assert response.status_code == 200
    assert ContactSubmission.objects.count() == 2
    assert "Please wait" in response.content.decode()


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_NOTIFICATION_EMAIL="owner@example.com",
)
def test_contact_sends_notification_when_configured(client):
    cache.clear()
    mail.outbox.clear()
    client.post(
        reverse("contact:index"),
        _contact_payload(),
        HTTP_HX_REQUEST="true",
        REMOTE_ADDR="127.0.0.1",
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["owner@example.com"]


def test_client_ip_prefers_first_x_forwarded_for_value_when_trusted():
    from django.test import RequestFactory

    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.7, 10.0.0.2",
    )
    with override_settings(CONTACT_TRUST_X_FORWARDED_FOR=True):
        assert client_ip(request) == "203.0.113.7"


def test_client_ip_ignores_x_forwarded_when_proxy_not_trusted():
    from django.test import RequestFactory

    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.7",
        REMOTE_ADDR="198.51.100.1",
    )
    with override_settings(CONTACT_TRUST_X_FORWARDED_FOR=False):
        assert client_ip(request) == "198.51.100.1"


def test_client_ip_falls_back_to_remote_addr():
    from django.test import RequestFactory

    request = RequestFactory().get("/", REMOTE_ADDR="198.51.100.1")
    assert client_ip(request) == "198.51.100.1"


@pytest.mark.django_db
def test_contact_non_htmx_post_redirects_on_success(client):
    cache.clear()
    response = client.post(reverse("contact:index"), _contact_payload(), follow=False)
    assert response.status_code == 302
    assert response.url == reverse("contact:index")
    assert ContactSubmission.objects.count() == 1


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_NOTIFICATION_EMAIL="owner@example.com",
)
def test_contact_save_succeeds_when_notification_email_fails(client):
    cache.clear()
    mail.outbox.clear()
    with patch("contact.views.send_mail", side_effect=OSError("smtp down")):
        response = client.post(
            reverse("contact:index"),
            _contact_payload(),
            HTTP_HX_REQUEST="true",
            REMOTE_ADDR="127.0.0.1",
        )
    assert response.status_code == 200
    assert ContactSubmission.objects.count() == 1
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_contact_rate_limit_is_per_ip(client, settings):
    cache.clear()
    settings.CONTACT_RATE_LIMIT_MAX = 1
    settings.CONTACT_RATE_LIMIT_WINDOW = 600
    url = reverse("contact:index")
    assert (
        client.post(
            url,
            _contact_payload(email="a@example.com"),
            HTTP_HX_REQUEST="true",
            REMOTE_ADDR="10.0.0.1",
        ).status_code
        == 200
    )
    assert (
        client.post(
            url,
            _contact_payload(email="b@example.com"),
            HTTP_HX_REQUEST="true",
            REMOTE_ADDR="10.0.0.2",
        ).status_code
        == 200
    )
    assert ContactSubmission.objects.count() == 2

