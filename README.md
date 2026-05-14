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
| `SECRET_KEY` | Django secret key. **`base`** uses a local default if unset; **`prod`** sets `SECRET_KEY = env("SECRET_KEY")` (no default) and **rejects** the known dev default string so you cannot ship with the placeholder secret. |
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
| `CONTACT_TRUST_X_FORWARDED_FOR` | In **`base` (dev)** defaults to `False` (only `REMOTE_ADDR` for rate limits / stored IP). In **`prod`** it defaults to **`True`** so Railway-style reverse proxies can supply `X-Forwarded-For`. Set to `False` in production if the app is not behind a trusted proxy. |
| `PUBLIC_GITHUB_URL` | Footer and contact “GitHub” link URL. |
| `PUBLIC_LINKEDIN_URL` | Footer and contact “LinkedIn” link URL. |
| `PUBLIC_CONTACT_EMAIL` | Shown in the footer and contact page; used in `mailto:` links. |
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

## Continuous integration

GitHub Actions runs the test suite on push and pull request to `main` or `master` (see `.github/workflows/ci.yml`).

## Architecture notes

Architecture decisions are recorded as ADRs under `docs/adr/` (for example HTMX vs React, slug strategy, SQLite dev vs Postgres prod).

## Deploying to Railway

1. Set `DJANGO_SETTINGS_MODULE=portfolio_site.settings.prod`.
2. Set **`SECRET_KEY`** in the host environment to a **new random value** (production uses `SECRET_KEY = env("SECRET_KEY")` with no fallback and **rejects** the local dev default string). Also set `ALLOWED_HOSTS`, `DATABASE_URL`, and `CANONICAL_URL`.
3. Set `PUBLIC_GITHUB_URL`, `PUBLIC_LINKEDIN_URL`, and `PUBLIC_CONTACT_EMAIL` to your real links and email when you want them on the public site.
4. **`CONTACT_TRUST_X_FORWARDED_FOR`** defaults to **`True` in production** so client IP for the contact form follows the first `X-Forwarded-For` hop (typical behind Railway’s proxy). Set it to **`False`** only if the app is not behind a trusted reverse proxy.
5. Optional: set `CONTACT_NOTIFICATION_EMAIL` and a real `EMAIL_BACKEND` if you want email alerts for contact form submissions.
6. Railway uses `railway.toml` or the `Procfile` start command to run migrations, collect static files, and launch Gunicorn.
