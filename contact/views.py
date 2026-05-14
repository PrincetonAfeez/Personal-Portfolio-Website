"""Views for the contact app."""

from __future__ import annotations

import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import ContactSubmissionForm

logger = logging.getLogger(__name__)


def client_ip(request: HttpRequest) -> str | None:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _contact_rate_key(request: HttpRequest) -> str:
    return f"contact:rl:{client_ip(request) or 'unknown'}"


def _contact_rate_limited(request: HttpRequest) -> bool:
    return cache.get(_contact_rate_key(request), 0) >= settings.CONTACT_RATE_LIMIT_MAX


def _contact_rate_bump(request: HttpRequest) -> None:
    key = _contact_rate_key(request)
    try:
        cache.incr(key)
    except ValueError:
        cache.add(key, 1, timeout=settings.CONTACT_RATE_LIMIT_WINDOW)


def _honeypot_filled(request: HttpRequest) -> bool:
    return bool(request.POST.get("referral_source", "").strip())


def _notify_contact_submission(submission) -> None:
    recipient = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", None)
    if not recipient:
        return
    try:
        send_mail(
            subject=f"[Portfolio] Contact from {submission.name}",
            message=(
                f"Name: {submission.name}\n"
                f"Email: {submission.email}\n\n"
                f"{submission.message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
        )
    except Exception:
        logger.exception("Contact notification email failed")


def _success_response(request: HttpRequest, *, flash_message: bool) -> HttpResponse:
    if flash_message:
        messages.success(request, "Thanks. Your note has been saved.")
    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "contact/partials/_contact_form.html",
            {"form": ContactSubmissionForm(), "success": True},
        )
    return redirect("contact:index")


def contact(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        if _honeypot_filled(request):
            return _success_response(request, flash_message=False)
        form = ContactSubmissionForm(request.POST)
        if form.is_valid():
            if _contact_rate_limited(request):
                form.add_error(
                    None,
                    "Please wait a few minutes before sending another message.",
                )
            else:
                submission = form.save(commit=False)
                submission.ip_address = client_ip(request)
                submission.save()
                _notify_contact_submission(submission)
                _contact_rate_bump(request)
                return _success_response(request, flash_message=True)
    else:
        form = ContactSubmissionForm()

    template = (
        "contact/partials/_contact_form.html"
        if request.headers.get("HX-Request") == "true"
        else "contact/contact.html"
    )
    return render(request, template, {"form": form})
