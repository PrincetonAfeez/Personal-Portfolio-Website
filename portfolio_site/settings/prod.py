"""Production settings for the portfolio site."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

_DEV_INSECURE_DEFAULT = "django-insecure-local-portfolio-build-key"

DEBUG = False

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31_536_000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# No default: must be present in the environment (django-environ raises if unset).
SECRET_KEY = env("SECRET_KEY")
if not str(SECRET_KEY).strip():
    raise ImproperlyConfigured("SECRET_KEY must be non-empty when using production settings.")
if str(SECRET_KEY).strip() == _DEV_INSECURE_DEFAULT:
    raise ImproperlyConfigured(
        "Production SECRET_KEY must not use the local development default. "
        "Set a unique secret in your host environment (for example `python -c \"import secrets; print(secrets.token_urlsafe(50))\"`)."
    )

# Default True: typical PaaS (e.g. Railway) sits behind a reverse proxy that sets
# X-Forwarded-For correctly. Set CONTACT_TRUST_X_FORWARDED_FOR=False if not.
CONTACT_TRUST_X_FORWARDED_FOR = env.bool("CONTACT_TRUST_X_FORWARDED_FOR", default=True)
