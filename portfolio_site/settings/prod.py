"""Production settings for the portfolio site."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .required_env import MissingEnvVarError, require_non_empty_str


DEBUG = False

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31_536_000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

try:
    SECRET_KEY = require_non_empty_str("SECRET_KEY")
except MissingEnvVarError as exc:
    raise ImproperlyConfigured(
        "SECRET_KEY must be set to a non-empty value in the environment when using "
        "production settings (it is not read from django-environ defaults here)."
    ) from exc

