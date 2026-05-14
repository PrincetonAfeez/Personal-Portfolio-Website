# Personal Portfolio Website

A Django + HTMX personal portfolio website. The site is a server-rendered monolith with no JavaScript framework or API layer.

## Stack

- Python 3.12 target, Django 5.2
- HTMX 2.0.10 from CDN with SRI
- Tailwind standalone CLI workflow, compiled to `static/css/site.css`
- SQLite in development, Postgres-ready through `DATABASE_URL`
- easy-thumbnails, django-environ, whitenoise
- pytest + pytest-django

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_portfolio
.\.venv\Scripts\python manage.py runserver
```

The current machine only exposes Python 3.14, so this build was verified locally with that interpreter while keeping the project target documented as Python 3.12.

## Environment variables

Copy `.env.example` to `.env` and adjust values.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key (required outside local defaults). |
| `DEBUG` | Enables debug mode; must be false in production. |
| `ALLOWED_HOSTS` | Comma-separated hostnames. |
| `DATABASE_URL` | Database URL (SQLite file URL in dev, Postgres in prod). |
| `CANONICAL_URL` | Site base URL for SEO (`link rel="canonical"`, `og:url`, robots sitemap line). No trailing slash issues are normalized in code. |
| `LOG_LEVEL` | Root logger level (for example `INFO`). |
| `DEFAULT_FROM_EMAIL` | From address for outbound mail. |
| `EMAIL_BACKEND` | Django mail backend (console in dev). |
| `CONTACT_NOTIFICATION_EMAIL` | If set, contact form sends a notification to this address after each save. |
| `CONTACT_RATE_LIMIT_WINDOW` | Rate limit window in seconds for contact submissions per IP (default `900`). |
| `CONTACT_RATE_LIMIT_MAX` | Max submissions per IP per window (default `5`). |
| `SECURE_SSL_REDIRECT` | Production: redirect HTTP to HTTPS. |
| `SECURE_HSTS_SECONDS` | Production HSTS max-age in seconds. |

## Tailwind standalone

Use the standalone Tailwind binary and compile into the checked-in CSS target:

```powershell
tailwindcss -i .\assets\tailwind\input.css -o .\static\css\site.css --minify
```

The current `site.css` is committed so the app runs without Node or a build step.

## Tests

Tests live next to apps (`tests.py`, `test_*.py`) and under `portfolio_site/`. Pytest is configured in `pyproject.toml`.

```powershell
.\.venv\Scripts\python -m pytest
```

For more detail on failures:

```powershell
.\.venv\Scripts\python -m pytest -vv --tb=short
```

## Architecture notes

Architecture decisions are recorded as ADRs under `docs/adr/` (for example HTMX vs React, slug strategy, SQLite dev vs Postgres prod).

## Deploying to Railway

1. Set `DJANGO_SETTINGS_MODULE=portfolio_site.settings.prod`.
2. Set `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, and `CANONICAL_URL`.
3. Optional: set `CONTACT_NOTIFICATION_EMAIL` and a real `EMAIL_BACKEND` if you want email alerts for contact form submissions.
4. Railway uses `railway.toml` or the `Procfile` start command to run migrations, collect static files, and launch Gunicorn.
