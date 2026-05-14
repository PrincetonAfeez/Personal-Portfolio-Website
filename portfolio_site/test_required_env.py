import pytest

from portfolio_site.settings.required_env import MissingEnvVarError, require_non_empty_str


def test_require_non_empty_str_returns_value(monkeypatch):
    monkeypatch.setenv("MY_VAR", "  ok  ")
    assert require_non_empty_str("MY_VAR") == "ok"


def test_require_non_empty_str_raises_when_missing(monkeypatch):
    monkeypatch.delenv("MY_VAR", raising=False)
    with pytest.raises(MissingEnvVarError) as exc_info:
        require_non_empty_str("MY_VAR")
    assert exc_info.value.name == "MY_VAR"


def test_require_non_empty_str_raises_when_blank(monkeypatch):
    monkeypatch.setenv("MY_VAR", "   ")
    with pytest.raises(MissingEnvVarError):
        require_non_empty_str("MY_VAR")
