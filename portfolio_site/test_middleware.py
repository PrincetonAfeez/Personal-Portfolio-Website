"""Tests for the middleware."""

from __future__ import annotations

from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from portfolio_site.middleware import RequestTimingMiddleware


def test_request_timing_middleware_adds_csp_when_response_lacks_it():
    def get_response(request):
        return HttpResponse("ok")

    request = RequestFactory().get("/")
    mw = RequestTimingMiddleware(get_response)

    with override_settings(CONTENT_SECURITY_POLICY="default-src 'self'"):
        response = mw(request)

    assert response["Content-Security-Policy"] == "default-src 'self'"


def test_request_timing_middleware_skips_csp_when_empty_setting():
    def get_response(request):
        return HttpResponse("ok")

    request = RequestFactory().get("/")
    mw = RequestTimingMiddleware(get_response)

    with override_settings(CONTENT_SECURITY_POLICY=""):
        response = mw(request)

    assert "Content-Security-Policy" not in response


def test_request_timing_middleware_preserves_existing_csp_header():
    def get_response(request):
        resp = HttpResponse("ok")
        resp["Content-Security-Policy"] = "default-src 'none'"
        return resp

    request = RequestFactory().get("/")
    mw = RequestTimingMiddleware(get_response)

    with override_settings(CONTENT_SECURITY_POLICY="default-src 'self'"):
        response = mw(request)

    assert response["Content-Security-Policy"] == "default-src 'none'"


def test_request_timing_middleware_adds_duration_header_when_debug():
    def get_response(request):
        return HttpResponse("ok")

    request = RequestFactory().get("/")
    mw = RequestTimingMiddleware(get_response)

    with override_settings(DEBUG=True, CONTENT_SECURITY_POLICY=""):
        response = mw(request)

    assert "X-Request-Duration-ms" in response


def test_request_timing_middleware_no_duration_header_when_not_debug():
    def get_response(request):
        return HttpResponse("ok")

    request = RequestFactory().get("/")
    mw = RequestTimingMiddleware(get_response)

    with override_settings(DEBUG=False, CONTENT_SECURITY_POLICY=""):
        response = mw(request)

    assert "X-Request-Duration-ms" not in response
