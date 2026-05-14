"""Small helpers for reading required environment variables (no Django imports)."""

from __future__ import annotations

import os


class MissingEnvVarError(Exception):
    """Raised when a required environment variable is missing or blank."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name


def require_non_empty_str(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise MissingEnvVarError(name)
    return value
