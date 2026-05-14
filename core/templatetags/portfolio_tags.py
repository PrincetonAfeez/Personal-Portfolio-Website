"""Template tags for the portfolio site."""

from __future__ import annotations

from math import ceil

import bleach
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from markdown import markdown

register = template.Library()


ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union(
    {
        "p",
        "pre",
        "span",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "img",
        "hr",
        "br",
    }
)
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "loading", "width", "height"],
    "code": ["class"],
    "span": ["class"],
}


@register.filter
@stringfilter
def markdownify(value: str) -> str:
    html = markdown(value, extensions=["extra", "sane_lists"])
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    return mark_safe(cleaned)


@register.filter
@stringfilter
def reading_time(value: str) -> str:
    words = len(value.split())
    minutes = max(1, ceil(words / 220))
    return f"{minutes} min read"


@register.simple_tag(takes_context=True)
def active_nav(context, section: str) -> str:
    request = context.get("request")
    if request is None:
        return ""

    path = request.path
    matches = {
        "home": path == "/",
        "projects": path.startswith("/projects/"),
        "about": path.startswith("/about/"),
        "contact": path.startswith("/contact/"),
        "resume": path.startswith("/resume/"),
    }
    return "nav-link--active" if matches.get(section, False) else ""

