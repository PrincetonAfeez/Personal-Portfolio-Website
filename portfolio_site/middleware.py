"""Middleware for the portfolio site."""

from time import perf_counter

from django.conf import settings


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = perf_counter()
        response = self.get_response(request)

        if settings.DEBUG:
            duration_ms = (perf_counter() - started_at) * 1000
            response["X-Request-Duration-ms"] = f"{duration_ms:.2f}"

        if getattr(settings, "CONTENT_SECURITY_POLICY", "") and "Content-Security-Policy" not in response:
            response["Content-Security-Policy"] = settings.CONTENT_SECURITY_POLICY

        return response
