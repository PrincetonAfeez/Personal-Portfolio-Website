"""Tests for the portfolio tags."""

from __future__ import annotations

import pytest
from django.template import Context, Template
from django.test import RequestFactory


@pytest.mark.parametrize(
    ("body", "forbidden"),
    [
        ("# Hi\n\n<script>alert(1)</script>", "<script"),
        ("[x](javascript:alert(1))", "javascript:"),
        ("<img src=x onerror=alert(1)>", "onerror"),
    ],
)
def test_markdownify_sanitizes_unsafe_content(body: str, forbidden: str):
    from core.templatetags.portfolio_tags import markdownify

    out = str(markdownify(body))
    assert forbidden.lower() not in out.lower()


def test_markdownify_allows_safe_markdown():
    from core.templatetags.portfolio_tags import markdownify

    out = str(markdownify("# Title\n\nParagraph with **bold**."))
    assert "Title" in out
    assert "bold" in out or "strong" in out


def test_reading_time_minimum_one_minute():
    from core.templatetags.portfolio_tags import reading_time

    assert reading_time("") == "1 min read"
    assert reading_time("hello") == "1 min read"


def test_reading_time_scales_with_word_count():
    from core.templatetags.portfolio_tags import reading_time

    words = "word " * 500
    assert reading_time(words) == "3 min read"


@pytest.mark.parametrize(
    ("path", "section", "expected_class"),
    [
        ("/", "home", "nav-link--active"),
        ("/projects/", "projects", "nav-link--active"),
        ("/about/", "about", "nav-link--active"),
        ("/contact/", "contact", "nav-link--active"),
        ("/resume/", "resume", "nav-link--active"),
        ("/projects/", "about", ""),
        ("/", "projects", ""),
    ],
)
def test_active_nav_matches_path(path: str, section: str, expected_class: str):
    request = RequestFactory().get(path)
    template = Template(
        f"{{% load portfolio_tags %}}{{% active_nav '{section}' %}}"
    )
    rendered = template.render(Context({"request": request})).strip()
    if expected_class:
        assert rendered == expected_class
    else:
        assert rendered == ""


def test_active_nav_without_request_returns_empty():
    template = Template("{% load portfolio_tags %}{% active_nav 'home' %}")
    assert template.render(Context({})).strip() == ""
