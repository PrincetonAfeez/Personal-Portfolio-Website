"""Context processors for the core app."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest


def canonical_urls(request: HttpRequest) -> dict[str, str]:
    base = str(settings.CANONICAL_URL).rstrip("/")
    path = request.path or "/"
    if not path.startswith("/"):
        path = f"/{path}"
    canonical_url = f"{base}{path}"
    return {"canonical_url": canonical_url, "site_origin": base}
