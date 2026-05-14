"""Development settings for the portfolio site."""

from .base import *  # noqa: F403


DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE  # noqa: F405
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
]
