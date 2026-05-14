# Architecture Decision Record
## App — Personal Portfolio Website
**Portfolio Platform Group | Document 1 of 5**
**Status: Accepted**

---

## Context

The Personal Portfolio Website is a Django + HTMX portfolio site for presenting hospitality-technology work, Python projects, professional background, and a contact workflow. The application is a server-rendered monolith, not a JavaScript SPA and not an API-backed frontend. It uses Django templates, Django ORM models, class-based project views, an HTMX-enhanced project archive and contact form, Tailwind standalone CSS output, Markdown rendering with HTML sanitization, thumbnail generation, and Railway-ready production configuration.

The repository’s own README describes the project as a Django + HTMX personal portfolio website with no JavaScript framework or API layer. The implementation confirms that direction: `manage.py` defaults to `portfolio_site.settings.dev`, the app stack is split across `core`, `projects`, `about`, and `contact`, and production behavior is configured through `portfolio_site.settings.prod`.

The decision was to build a production-shaped Django portfolio that demonstrates web architecture, content modeling, project publication workflow, contact handling, SEO routes, deployment readiness, and testing without adding unnecessary frontend complexity.

---

## Decisions

### Decision 1 — Django + HTMX monolith instead of a JavaScript frontend

**Chosen:** Django 5.2 with server-rendered templates and HTMX-enhanced interactions.

**Rejected:** React/Next.js, a separate frontend application, or a JSON API layer.

**Reason:** The portfolio’s purpose is to demonstrate Python, Django, HTMX, database-backed content, and operational software thinking. A separate JavaScript app would add build complexity and shift attention away from the project’s actual learning focus. HTMX supports partial updates for project filtering/pagination and contact form submission while keeping the request/response model in Django.

---

### Decision 2 — Separate apps for core pages, projects, about content, and contact

**Chosen:** The Django project uses:
- `core` for home/about/resume/robots/errors/context/template tags/sitemaps
- `projects` for project catalogue models, views, services, URLs, sitemap, and seed command
- `about` for skills and timeline entries
- `contact` for contact submissions, form validation, rate limiting, and optional notification email

**Rejected:** A single “portfolio” app containing all models, views, and forms.

**Reason:** The site has several distinct concerns. Project publishing, contact submission handling, about-page timeline/skills, and global page infrastructure should not be mixed in one module. The split keeps each app small enough to reason about while still preserving a monolithic deployment model.

---

### Decision 3 — Database-backed project catalogue

**Chosen:** Use `Project`, `Tag`, and `TechStack` models. `Project` has many-to-many relationships with tags and tech-stack items, plus publication status, feature flags, publication dates, hero image metadata, repository/demo links, and Markdown body content.

**Rejected:** Hardcoded project cards in templates or a static YAML-only project list.

**Reason:** A portfolio catalogue benefits from publication workflow, filtering, featured projects, tag pages, adjacent project navigation, sitemaps, and future growth. Django models make those behaviors queryable and testable. Static template content would be simpler, but it would not demonstrate database modeling or allow clean published/featured/tagged querysets.

---

### Decision 4 — Custom queryset and manager methods for project publication rules

**Chosen:** `ProjectQuerySet` defines `published()`, `featured()`, and `by_tag()`.

**Rejected:** Repeating publication filters manually in every view or service.

**Reason:** Publication rules are central to the site. A project is public only when `is_published=True`, `published_at` is not null, and `published_at` is not in the future. Encoding that once in the queryset reduces duplication and protects views, sitemaps, featured project retrieval, and tag filtering from accidentally exposing draft or future content.

---

### Decision 5 — Auto-generated unique slugs

**Chosen:** Projects with blank slugs generate slugs from the title, adding numeric suffixes on collision.

**Rejected:** Requiring every project slug to be manually entered.

**Reason:** Manual slugs are still allowed, but automatic generation reduces friction and prevents duplicate slug failures for normal content creation. Collision handling keeps URLs stable and readable.

---

### Decision 6 — HTMX-enhanced project filtering and pagination

**Chosen:** Project list and tag-filter views return a full page for normal requests and `projects/partials/_project_grid.html` for HTMX requests. Filter chips use `hx-get`, `hx-target`, and `hx-push-url`. Pagination uses a “Load more” link with HTMX enhancement.

**Rejected:** Full-page-only filtering/pagination or custom JavaScript.

**Reason:** The project archive is the most natural place for progressive enhancement. HTMX keeps navigation server-owned, allows browser URLs to update, and returns HTML fragments rather than JSON. This supports the “no frontend framework” decision while still creating a more fluid browsing experience.

---

### Decision 7 — Server-side Markdown rendering with sanitization

**Chosen:** Project body text is rendered through a `markdownify` template filter using `markdown`, then cleaned with `bleach` before being marked safe.

**Rejected:** Rendering raw Markdown HTML without sanitization or storing pre-rendered HTML.

**Reason:** Project writeups need formatting, headings, lists, and code-like content. Markdown gives authoring flexibility, but raw HTML output must be sanitized before rendering in templates. `bleach` provides a controlled allowlist of tags, attributes, and protocols.

---

### Decision 8 — Contact form with honeypot, rate limiting, persistence, and optional notification

**Chosen:** The contact workflow stores `ContactSubmission` rows, records client IP, includes a honeypot field, rate-limits submissions by IP through Django cache, optionally sends a notification email, and supports HTMX partial success/error rendering.

**Rejected:** Simple `mailto:` only or unprotected form submission.

**Reason:** A real contact form demonstrates form handling, database persistence, user feedback, spam resistance, cache-backed rate limiting, email integration, and graceful failure. The form saves messages even if optional notification email fails.

---

### Decision 9 — Tailwind standalone workflow with committed compiled CSS

**Chosen:** Tailwind is compiled from `assets/tailwind/input.css` into `static/css/site.css`, and the compiled CSS is committed.

**Rejected:** Node-based frontend build requirement for every run or Tailwind Play CDN.

**Reason:** The site should run without Node or an active build step once CSS is compiled. The standalone Tailwind workflow keeps frontend tooling light and still supports utility-based styling.

---

### Decision 10 — SQLite in development, Postgres-ready production database URL

**Chosen:** `DATABASE_URL` is parsed by `django-environ`, defaulting to local SQLite but allowing PostgreSQL in production.

**Rejected:** Hardcoded SQLite everywhere or hardcoded PostgreSQL everywhere.

**Reason:** SQLite makes local setup fast. PostgreSQL readiness supports Railway deployment and production expectations. The project remains portable because the database is controlled by environment variables.

---

### Decision 11 — Railway/Gunicorn/WhiteNoise deployment path

**Chosen:** Railway runs migrations, collects static files, and starts Gunicorn. WhiteNoise serves compressed manifest static files.

**Rejected:** Manual VPS deployment or relying on Django’s development server.

**Reason:** Railway is appropriate for a small production portfolio. Gunicorn is a production WSGI server. WhiteNoise keeps static serving simple without a separate static host. Running migrations and collectstatic at startup/deploy time makes deployment self-contained.

---

## Consequences

**Positive:**
- The site honestly demonstrates Django and HTMX architecture.
- Project content is structured, publishable, filterable, and sitemap-aware.
- Contact handling goes beyond a decorative page and demonstrates real web-form concerns.
- Markdown writeups are flexible but sanitized.
- HTMX improves browsing and form submission without a JavaScript framework.
- Tailwind output is committed so the site can run without Node.
- Deployment configuration is simple and Railway-compatible.
- Tests cover publication rules, slugs, sitemaps, HTMX partials, contact workflows, canonical URLs, robots.txt, and error pages.

**Negative / Trade-offs:**
- The site is heavier than a static portfolio.
- SQLite development and Postgres production can diverge in subtle ways.
- HTMX from CDN requires CSP allowances for `https://unpkg.com`.
- The current CSP includes `unsafe-inline`, which is convenient but weaker than a nonce/hash/self-host-only policy.
- The seed command generates sample content and static files, but it is not a general manifest-driven content system.
- Running migrations and collectstatic in the Railway start command is simple but can slow startup and is less controlled than a separate release phase.

---

## Alternatives Not Explored

- **Static site generator:** Rejected because database-backed projects, contact persistence, and HTMX interactions are part of the learning goal.
- **Full CMS:** Not needed for the current owner-maintained portfolio.
- **Vendored HTMX instead of CDN:** A good future hardening step that would allow stricter CSP.
- **Dedicated deployment release command:** A future improvement if the app grows beyond small-portfolio scale.
- **PostgreSQL-only local development:** More production-like, but less friendly for quick local setup.

---

*Constitution reference: Article 1 (architectural thinking), Article 3.4 (larger project classification), Article 4 (engineering quality), Article 6 (behavior verification), and Article 7 (progressive complexity).*

---


# Technical Design Document
## App — Personal Portfolio Website
**Portfolio Platform Group | Document 2 of 5**

---

## Overview

Personal Portfolio Website is a Django + HTMX monolith for a hospitality-technology portfolio. It includes public marketing pages, a project archive, tag-filtered project browsing, project detail pages with Markdown-rendered bodies, an about page backed by skills and timeline models, a contact form with spam/rate-limit controls, canonical URL generation, robots.txt, sitemaps, custom error pages, request timing/CSP middleware, thumbnail aliases, Tailwind CSS, and Railway/Gunicorn deployment support.

**Project package:** `portfolio_site`  
**Django apps:** `core`, `projects`, `about`, `contact`  
**Default local settings:** `portfolio_site.settings.dev`  
**Production settings:** `portfolio_site.settings.prod`  
**Primary entry point:** `manage.py` / `portfolio_site.wsgi.application`  
**Primary templates directory:** `templates/`  
**Compiled CSS:** `static/css/site.css`  
**Tailwind source:** `assets/tailwind/input.css`

---

## Data Flow

### Home page

```text
GET /
  → portfolio_site.urls
  → core.views.home
  → projects.services.get_featured_projects()
  → Tag.objects.all()[:8]
  → templates/core/home.html
  → templates/base.html
  → HTML response
```

---

### Project archive

```text
GET /projects/
  → ProjectListView
  → Project.objects.published().prefetch_related("tags", "tech_stack")
  → ListView pagination, 9 per page
  → normal request: templates/projects/index.html
  → HTMX request: templates/projects/partials/_project_grid.html
```

---

### Tag-filtered project archive

```text
GET /projects/tag/<tag_slug>/
  → TagDetailView(ProjectListView)
  → get_object_or_404(Tag, slug=tag_slug)
  → filter published projects by selected tag
  → full page or HTMX partial depending on HX-Request
```

---

### Project detail

```text
GET /projects/<slug>/
  → ProjectDetailView
  → Project.objects.published().prefetch_related("tags", "tech_stack")
  → get_adjacent_projects(project)
  → templates/projects/detail.html
  → project.body|markdownify
  → HTML response
```

---

### Contact form

```text
GET /contact/
  → contact.views.contact
  → ContactSubmissionForm()
  → templates/contact/contact.html

POST /contact/
  → honeypot check
  → ContactSubmissionForm(request.POST)
  → rate-limit check by client IP
  → save ContactSubmission with IP
  → optional send_mail notification
  → bump rate counter
  → HTMX request: partial form success response
  → normal request: redirect back to contact page
```

---

### Seeding sample content

```text
python manage.py seed_portfolio
  → generate static operations-map image
  → generate static resume PDF
  → upsert tags and tech-stack rows
  → upsert skills and timeline rows
  → upsert sample projects
  → create project hero images when missing
```

---

## Module-Level Structure

```text
Personal-Portfolio-Website/
  manage.py
  portfolio_site/
    settings/
      base.py
      dev.py
      prod.py
    urls.py
    middleware.py
    wsgi.py
    asgi.py
  core/
    views.py
    context_processors.py
    sitemaps.py
    templatetags/
      portfolio_tags.py
    tests.py
  projects/
    models.py
    views.py
    services.py
    urls.py
    sitemaps.py
    management/commands/
      seed_portfolio.py
    tests.py
  about/
    models.py
    tests.py
  contact/
    models.py
    forms.py
    views.py
    urls.py
    tests.py
  templates/
    base.html
    core/
    projects/
    about/
    contact/
  assets/
    tailwind/
      input.css
  static/
    css/site.css
    img/
    resume/
  requirements.txt
  requirements-dev.txt
  pyproject.toml
  railway.toml
  Procfile
```

---

## Module Dependency Graph

```text
manage.py
  └── portfolio_site.settings.dev by default

portfolio_site.settings.base
  ├── django-environ
  ├── easy_thumbnails
  ├── whitenoise
  ├── core
  ├── projects
  ├── about
  └── contact

portfolio_site.urls
  ├── core.views
  ├── projects.urls
  ├── contact.urls
  ├── core.sitemaps.StaticViewSitemap
  └── projects.sitemaps.ProjectSitemap

portfolio_site.middleware
  ├── time.perf_counter
  └── django.conf.settings

core.views
  ├── about.models.Skill / TimelineEntry
  ├── projects.models.Tag
  ├── projects.services.get_featured_projects
  └── django.shortcuts.render

core.context_processors
  └── django.conf.settings

core.templatetags.portfolio_tags
  ├── markdown.markdown
  ├── bleach.clean
  ├── reading_time
  └── active_nav

projects.models
  ├── django.db.models
  ├── django.urls.reverse
  ├── django.utils.timezone
  └── django.utils.text.slugify

projects.views
  ├── ProjectListView
  ├── TagDetailView
  ├── ProjectDetailView
  ├── projects.models.Project / Tag
  └── projects.services.get_adjacent_projects

projects.services
  ├── django.db.models.Q
  └── projects.models.Project

projects.management.commands.seed_portfolio
  ├── Pillow Image / ImageDraw / ImageFont
  ├── about.models.Skill / TimelineEntry
  ├── projects.models.Project / Tag / TechStack
  └── django.core.files ContentFile

contact.forms
  └── contact.models.ContactSubmission

contact.views
  ├── django.core.cache.cache
  ├── django.core.mail.send_mail
  ├── django.contrib.messages
  ├── ContactSubmissionForm
  └── ContactSubmission
```

---

## Core Data Structures

### `ProjectQuerySet`

Custom queryset methods:

```python
published()
featured()
by_tag(slug)
```

`published()` filters to:
- `is_published=True`
- `published_at` not null
- `published_at <= timezone.now()`

and orders by:
```python
-published_at, -created_at
```

---

### `Tag`

```python
name = CharField(max_length=80, unique=True)
slug = SlugField(max_length=90, unique=True)
description = TextField(blank=True)
```

Ordering:
```python
["name"]
```

---

### `TechStack`

```python
name = CharField(max_length=80, unique=True)
slug = SlugField(max_length=90, unique=True)
category = CharField(max_length=20, choices=Category.choices)
```

Categories:
- language
- framework
- tool
- service

Ordering:
```python
["category", "name"]
```

---

### `Project`

```python
title = CharField(max_length=180)
slug = SlugField(max_length=200, unique=True, blank=True)
summary = TextField()
body = TextField()
hero_image = ImageField(upload_to="projects/heroes/", blank=True)
hero_alt = CharField(max_length=200, blank=True)
tags = ManyToManyField(Tag, related_name="projects", blank=True)
tech_stack = ManyToManyField(TechStack, related_name="projects", blank=True)
is_published = BooleanField(default=False)
is_featured = BooleanField(default=False)
published_at = DateTimeField(null=True, blank=True)
repo_url = URLField(blank=True)
demo_url = URLField(blank=True)
created_at = DateTimeField(auto_now_add=True)
updated_at = DateTimeField(auto_now=True)
```

Important methods:
- `save()` auto-generates slug when blank
- `get_absolute_url()`
- `_build_unique_slug()`

---

### `Skill`

```python
name = CharField(max_length=80)
category = CharField(max_length=80)
months_of_use = PositiveSmallIntegerField(default=0)
proficiency = PositiveSmallIntegerField(default=3)
```

Ordering:
```python
["category", "-proficiency", "name"]
```

---

### `TimelineEntry`

```python
date = DateField()
title = CharField(max_length=140)
description = TextField()
entry_type = CharField(max_length=20, choices=EntryType.choices)
```

Entry types:
- learning
- work
- project

Ordering:
```python
["-date"]
```

---

### `ContactSubmission`

```python
name = CharField(max_length=120)
email = EmailField()
message = TextField()
submitted_at = DateTimeField(auto_now_add=True)
ip_address = GenericIPAddressField(null=True, blank=True)
```

Ordering:
```python
["-submitted_at"]
```

---

### `ContactSubmissionForm`

Model form over:
- name
- email
- message

Additional non-model honeypot field:
```python
referral_source
```

It is visually/semantically hidden through form template and has:
- `required=False`
- `autocomplete="off"`
- `tabindex="-1"`

---

## Function and Class Reference

### `manage.main()`

Sets:
```python
DJANGO_SETTINGS_MODULE = "portfolio_site.settings.dev"
```

and delegates to Django’s command-line executor.

---

### `RequestTimingMiddleware`

Responsibilities:
- measure request duration with `perf_counter()`
- add `X-Request-Duration-ms` header only when `settings.DEBUG` is true
- add `Content-Security-Policy` header when configured and not already present

---

### `canonical_urls(request)`

Builds:
```python
canonical_url = settings.CANONICAL_URL.rstrip("/") + request.path
site_origin = settings.CANONICAL_URL.rstrip("/")
```

Returns:
```python
{"canonical_url": canonical_url, "site_origin": base}
```

---

### `core.views.home(request)`

Renders `core/home.html` with:
- featured projects
- first 8 tags
- page title
- meta description

---

### `core.views.about(request)`

Renders `about/about.html` with:
- all skills
- all timeline entries
- page title
- meta description

---

### `core.views.resume(request)`

Renders `core/resume.html`.

---

### `core.views.robots_txt(request)`

Returns a `TemplateResponse` using `templates/core/robots.txt` and `settings.CANONICAL_URL`.

---

### `core.views.handler404()` and `handler500()`

Render custom 404 and 500 templates.

---

### `markdownify(value)`

Pipeline:
1. `markdown(value, extensions=["extra", "sane_lists"])`
2. `bleach.clean(...)` with explicit tag/attribute/protocol allowlists
3. `mark_safe(cleaned)`

---

### `reading_time(value)`

Counts words, divides by 220 words/minute, rounds up, and returns:
```text
N min read
```

Minimum:
```text
1 min read
```

---

### `active_nav(context, section)`

Returns:
```text
nav-link--active
```

when the current request path matches a known section.

Sections:
- home
- projects
- about
- contact
- resume

---

### `Project.save()`

If `slug` is blank, calls `_build_unique_slug()` before saving.

---

### `Project._build_unique_slug()`

Builds slug from title, limits base length, checks for collisions, and appends `-2`, `-3`, etc. until unique.

---

### `Project.get_absolute_url()`

Returns:
```text
/projects/<slug>/
```

---

### `get_featured_projects(limit=3)`

Returns up to 3 featured published projects with tags and tech stack prefetched.

---

### `get_adjacent_projects(project)`

Returns:
```python
(previous_project, next_project)
```

based on published ordering and created-at tie-breakers.

---

### `ProjectListView`

- model: `Project`
- page size: 9
- context name: `projects`
- normal template: `projects/index.html`
- HTMX template: `projects/partials/_project_grid.html`

Adds:
- tags
- selected tag
- page title
- meta description

---

### `TagDetailView`

Subclass of `ProjectListView`. Uses the same logic with a tag slug in the URL.

---

### `ProjectDetailView`

- uses only published projects
- prefetches tags and tech stack
- adds previous and next projects
- sets page title and meta description

---

### `ProjectSitemap`

Returns `Project.objects.published()` and uses `updated_at` as last modified.

---

### `StaticViewSitemap`

Returns:
- home
- projects index
- about
- contact
- resume

---

### `client_ip(request)`

Prefers first `HTTP_X_FORWARDED_FOR` value. Falls back to `REMOTE_ADDR`.

---

### `_contact_rate_key(request)`

Builds cache key:
```text
contact:rl:<client_ip or unknown>
```

---

### `_contact_rate_limited(request)`

Returns true when current cache counter is at or above `CONTACT_RATE_LIMIT_MAX`.

---

### `_contact_rate_bump(request)`

Increments the cache counter or initializes it with `CONTACT_RATE_LIMIT_WINDOW` timeout.

---

### `_honeypot_filled(request)`

Returns true if `referral_source` has submitted content.

---

### `_notify_contact_submission(submission)`

If `CONTACT_NOTIFICATION_EMAIL` is set, sends a notification email. Exceptions are logged and do not prevent the submission from succeeding.

---

### `_success_response(request, flash_message)`

For HTMX:
- returns `contact/partials/_contact_form.html`
- passes a fresh form and `success=True`

For normal requests:
- optionally flashes a success message
- redirects to contact index

---

### `contact.views.contact(request)`

Handles GET and POST contact form flows. Supports both full-page and HTMX partial rendering.

---

### `seed_portfolio`

Creates sample content and assets:
- operations map image
- static resume PDF
- tags
- tech stack entries
- skills
- timeline entries
- projects
- project hero images

---

## Template Breakdown

### `templates/base.html`

Defines:
- canonical link
- page title and meta description
- Open Graph/Twitter metadata
- compiled CSS link
- HTMX CDN script with SRI
- skip link
- navigation
- message stack
- `main#page`
- footer

---

### `templates/projects/index.html`

Defines:
- project archive header
- tag filter chips
- HTMX-enhanced tag links
- project grid include

---

### `templates/projects/partials/_project_grid.html`

Defines:
- result count
- selected tag label
- project cards
- empty state
- “Load more” link enhanced with HTMX

---

### `templates/projects/detail.html`

Defines:
- hero image through easy-thumbnails
- reading time
- publication date
- repository/demo links
- tag rack
- Markdown-rendered project body
- adjacent project navigation

---

### `templates/contact/contact.html`

Defines:
- contact page copy
- direct links
- contact form partial include

---

### `templates/contact/partials/_contact_form.html`

Defines:
- success panel
- HTMX-enabled POST form
- CSRF token
- honeypot field
- field-level errors
- non-field errors
- submit button

---

## State Management

### Database state

Stored models:
- Project
- Tag
- TechStack
- Skill
- TimelineEntry
- ContactSubmission
- Django auth/admin/session tables

Local default:
```text
SQLite db.sqlite3
```

Production:
```text
DATABASE_URL, Postgres-ready
```

---

### Cache state

Django locmem cache stores contact form rate-limit counters.

Default backend:
```text
django.core.cache.backends.locmem.LocMemCache
```

---

### Static/media state

Static:
- compiled CSS
- generated operations map
- generated/static resume PDF
- general static assets

Media:
- uploaded project hero images
- generated seed project hero images saved through `ImageField`

---

### Environment/config state

Loaded by `django-environ` from process environment and `.env`.

Key settings:
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- DATABASE_URL
- CANONICAL_URL
- CONTACT_NOTIFICATION_EMAIL
- CONTACT_RATE_LIMIT_WINDOW
- CONTACT_RATE_LIMIT_MAX
- SECURE_SSL_REDIRECT
- SECURE_HSTS_SECONDS
- LOG_LEVEL
- EMAIL_BACKEND
- DEFAULT_FROM_EMAIL

---

## Error Handling Strategy

- Draft, future, or unpublished projects are excluded through queryset methods.
- Missing project detail slugs return 404.
- Missing tag slugs return 404.
- Invalid list pagination raises 404 through Django ListView behavior.
- Contact honeypot submissions return success without saving.
- Contact rate-limited submissions add non-field form error.
- Email notification failures are logged but do not block saved submissions.
- Missing static/media files are handled by normal static/media serving behavior.
- Custom 404 and 500 handlers render user-friendly templates.
- Production security settings enable SSL redirect, secure cookies, HSTS, X-Frame denial, and content-type nosniff.

---

## External Dependencies

### Runtime

| Dependency | Purpose |
|---|---|
| Django | Web framework |
| django-environ | Environment configuration and database URL parsing |
| easy-thumbnails | Thumbnail generation for project hero images |
| whitenoise | Static file serving |
| Markdown | Markdown-to-HTML rendering |
| bleach | HTML sanitization |
| pillow | Image generation and image handling |
| psycopg / psycopg-binary | PostgreSQL support |
| gunicorn | Production WSGI server |
| sqlparse, asgiref, tzdata, packaging, webencodings | Supporting runtime packages |

---

### Development / testing

| Dependency | Purpose |
|---|---|
| pytest | Test runner |
| pytest-django | Django integration for pytest |
| Pygments, colorama, iniconfig, pluggy | Test/dev support packages |

---

## Concurrency Model

The application is synchronous Django served by Gunicorn in production. It does not define async views, background workers, task queues, websockets, or threaded application logic.

Concurrent request handling is delegated to:
- Gunicorn worker process model
- Django request/response lifecycle
- database connection handling
- cache backend behavior

---

## Known Limitations

- HTMX is loaded from a CDN, not vendored.
- CSP allows `unsafe-inline` and `https://unpkg.com`.
- Contact rate limiting uses local memory cache by default, which is not shared across multiple processes/instances.
- Seed content is sample/demo content, not a canonical YAML manifest.
- Running migrations and collectstatic in the Railway start command is simple but not ideal for larger deployments.
- Contact notifications require email backend configuration.
- The footer/direct links use placeholder generic links in templates unless updated.
- The site target is Python 3.12, but README notes local verification on Python 3.14.
- There is no dedicated health-check endpoint.
- No CI workflow file was observed during this inspection; pytest is configured through `pyproject.toml`.

---

## Design Patterns Used

- Django MVT
- App-level separation of concerns
- QuerySet/Manager encapsulation
- Class-based views
- Service functions for reusable query logic
- HTMX progressive enhancement
- Template filters/tags for markdown, reading time, and active navigation
- Form object for validation and ModelForm persistence
- Cache-backed rate limiting
- Management command seeding
- Environment-based settings split
- Middleware for timing and CSP headers

---

## Verification Summary

The test suite verifies:
- project publication filtering
- featured project filtering
- tag-filtered project querysets
- slug generation and collision handling
- sitemap behavior for published projects
- combined sitemap static and dynamic URLs
- HTMX tag filter partial rendering
- adjacent project navigation
- unpublished project 404 behavior
- unknown tag 404 behavior
- project list pagination and invalid pages
- project detail smoke behavior
- contact form valid save behavior
- invalid contact form errors
- honeypot behavior
- rate limiting
- notification email behavior
- email failure tolerance
- per-IP rate limiting
- canonical URL context
- public URL smoke tests
- robots.txt canonical sitemap
- custom 404 and 500 handlers
- about page rendering

---

*Constitution reference: Article 4 (engineering quality), Article 6 (behavior verification), Article 7 (progressive complexity), and Article 8 (valid learner work).*

---


# Interface Design Specification
## App — Personal Portfolio Website
**Portfolio Platform Group | Document 3 of 5**

---

## Public Web Interface

| Method | Path | View / Handler | Success Status | Description |
|---|---|---|---:|---|
| GET | `/` | `core.views.home` | 200 | Home page with featured projects and tags |
| GET | `/projects/` | `ProjectListView` | 200 | Published project archive |
| GET | `/projects/?page=N` | `ProjectListView` | 200 | Paginated project archive |
| GET | `/projects/tag/<tag_slug>/` | `TagDetailView` | 200 | Tag-filtered project archive |
| GET | `/projects/<slug>/` | `ProjectDetailView` | 200 | Published project detail page |
| GET | `/about/` | `core.views.about` | 200 | About page with skills/timeline |
| GET | `/contact/` | `contact.views.contact` | 200 | Contact page/form |
| POST | `/contact/` | `contact.views.contact` | 200 or 302 | Contact form submission |
| GET | `/resume/` | `core.views.resume` | 200 | Resume page |
| GET | `/robots.txt` | `core.views.robots_txt` | 200 | Robots file |
| GET | `/sitemap.xml` | Django sitemap view | 200 | Static and project sitemap |
| GET | `/admin/` | Django admin | 200/302 | Admin interface |
| any | unknown route | custom 404 handler | 404 | Custom not-found page |
| server error | n/a | custom 500 handler | 500 | Custom server-error page |

---

## Invocation Syntax

### Development server

```powershell
.\.venv\Scripts\python manage.py runserver
```

or:

```bash
python manage.py runserver
```

Default settings:
```text
portfolio_site.settings.dev
```

---

### Production server

```bash
gunicorn portfolio_site.wsgi:application --log-file -
```

Railway/Procfile command also runs:
```bash
python manage.py migrate &&
python manage.py collectstatic --noinput &&
gunicorn portfolio_site.wsgi:application --log-file -
```

---

### Migrations

```bash
python manage.py migrate
```

---

### Seed demo content

```bash
python manage.py seed_portfolio
```

---

### Static files

```bash
python manage.py collectstatic --noinput
```

---

### Tailwind standalone build

```powershell
tailwindcss -i .\assets\tailwind\input.css -o .\static\css\site.css --minify
```

---

### Tests

```powershell
.\.venv\Scripts\python -m pytest
```

Verbose:

```powershell
.\.venv\Scripts\python -m pytest -vv --tb=short
```

---

## URL Input Contract

### `/projects/`

Query parameters:

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `page` | integer-like string | No | 1 | Page number for Django ListView pagination |

Headers:

| Header | Required | Accepted Value | Behavior |
|---|---|---|---|
| `HX-Request` | No | `true` | Returns project-grid partial instead of full page |

Page size:
```text
9
```

Invalid page values:
```text
404
```

---

### `/projects/tag/<tag_slug>/`

Path parameter:

| Name | Type | Required | Description |
|---|---|---|---|
| `tag_slug` | slug | Yes | Tag slug used to filter published projects |

Unknown tag:
```text
404
```

Supports the same `page` query parameter and `HX-Request` header as `/projects/`.

---

### `/projects/<slug>/`

Path parameter:

| Name | Type | Required | Description |
|---|---|---|---|
| `slug` | slug | Yes | Project slug |

Only published projects are available. Unpublished, future, or missing projects return 404.

---

### `/contact/` GET

No query parameters required. Returns full contact page unless requested as a partial through internal template flow.

---

### `/contact/` POST

Form fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Sender name |
| `email` | email | Yes | Sender email |
| `message` | text | Yes | Contact message |
| `referral_source` | string | No | Honeypot field; should remain empty |
| `csrfmiddlewaretoken` | string | Yes | Django CSRF token |

Headers:

| Header | Required | Accepted Value | Behavior |
|---|---|---|---|
| `HX-Request` | No | `true` | Returns form partial response instead of redirect |

---

## Output Contract

### Home page

Output includes:
- full HTML document
- canonical URL
- metadata
- featured projects
- tags
- global nav/footer
- compiled CSS
- HTMX script

---

### Project archive

Full request output:
- full HTML document
- project filter panel
- project grid
- page title and metadata

HTMX request output:
- `project-grid-shell`
- result count
- project cards
- empty state when no matches exist
- load-more link when there is a next page
- no `<!doctype html>` full layout

---

### Project detail

Output includes:
- project title
- summary
- hero image when present
- reading time
- publication date
- repository/demo links when present
- tags
- sanitized Markdown body
- previous/next project navigation

---

### Contact GET

Output includes:
- contact page
- direct links
- contact form
- CSRF token
- honeypot field

---

### Contact POST success

Normal request:
```text
302 redirect to /contact/
```

HTMX request:
```text
200 partial with success panel
```

Success panel copy includes:
```text
Message received
```

---

### Contact POST validation error

Output:
```text
200
```

Includes field errors or non-field errors in the form partial/full page.

---

### Honeypot submission

Output behaves like success but does not save a database row.

---

### Rate-limited contact submission

Output:
```text
200
```

Adds non-field error:
```text
Please wait a few minutes before sending another message.
```

---

### robots.txt

Output shape:

```text
User-agent: *
Allow: /

Sitemap: <CANONICAL_URL>/sitemap.xml
```

Content type:
```text
text/plain
```

---

## Exit Code Reference

The project does not define custom process exit codes.

| Command | Success | Failure |
|---|---:|---:|
| `python manage.py runserver` | 0 on clean process exit | non-zero on settings/import/startup errors |
| `python manage.py migrate` | 0 | non-zero on database/migration error |
| `python manage.py seed_portfolio` | 0 | non-zero on command/runtime/database/image error |
| `python manage.py collectstatic --noinput` | 0 | non-zero on static manifest/config error |
| `python -m pytest` | 0 | non-zero on test failure |
| `gunicorn portfolio_site.wsgi:application` | 0 on clean stop | non-zero on boot/runtime failure |
| `tailwindcss ...` | 0 | non-zero on Tailwind/build error |

---

## Environment Variables

| Variable | Required | Default / Behavior | Description |
|---|---|---|---|
| `SECRET_KEY` | Required outside local defaults | local insecure fallback | Django secret |
| `DEBUG` | No | false in base, true in dev | Debug mode |
| `ALLOWED_HOSTS` | Yes in production | localhost/testserver defaults | Comma-separated hostnames |
| `DATABASE_URL` | No locally, yes in production | local SQLite URL | Database connection |
| `CANONICAL_URL` | Recommended | `http://127.0.0.1:8000` | Base URL for canonical/OG/robots sitemap |
| `LOG_LEVEL` | No | `INFO` | Root logger level |
| `DEFAULT_FROM_EMAIL` | No | `portfolio@example.com` | Notification sender |
| `EMAIL_BACKEND` | No | console backend | Django email backend |
| `CONTACT_NOTIFICATION_EMAIL` | No | empty / disabled | Recipient for contact notifications |
| `CONTACT_RATE_LIMIT_WINDOW` | No | 900 | Rate-limit window in seconds |
| `CONTACT_RATE_LIMIT_MAX` | No | 5 | Max contact submissions per IP per window |
| `SECURE_SSL_REDIRECT` | Production | true in prod | Redirect HTTP to HTTPS |
| `SECURE_HSTS_SECONDS` | Production | 31536000 in prod | HSTS max age |

---

## Configuration Files

### `.env`

Loaded by:
```python
environ.Env.read_env(BASE_DIR / ".env")
```

Use `.env.example` as the local template.

---

### `requirements.txt`

Pinned runtime dependencies including:
- Django
- django-environ
- easy-thumbnails
- whitenoise
- Markdown
- bleach
- Pillow
- psycopg
- gunicorn

---

### `requirements-dev.txt`

Includes runtime requirements plus:
- pytest
- pytest-django
- dev/test support packages

---

### `pyproject.toml`

Configures pytest:
```text
DJANGO_SETTINGS_MODULE = portfolio_site.settings.dev
python_files = tests.py, test_*.py, *_tests.py
testpaths = about, core, contact, projects, portfolio_site
```

---

### `railway.toml`

Configures Railway:
- Nixpacks builder
- start command with migrate, collectstatic, and Gunicorn
- restart policy on failure
- max retries 3

---

### `Procfile`

Defines equivalent web process:
```text
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn portfolio_site.wsgi:application --log-file -
```

---

## Side Effects

| Operation | Side Effect |
|---|---|
| `python manage.py migrate` | Creates/updates database schema |
| `python manage.py seed_portfolio` | Creates sample DB content and writes static/media images/PDF |
| `python manage.py collectstatic` | Writes collected static files to `staticfiles/` |
| Contact form success | Creates `ContactSubmission` row |
| Contact form success with notification configured | Sends email notification |
| Contact form success | Increments per-IP rate-limit cache key |
| Contact honeypot submission | Returns success without saving |
| Request in DEBUG | Adds `X-Request-Duration-ms` header |
| Middleware response | Adds `Content-Security-Policy` if configured and absent |
| Tailwind build | Rewrites `static/css/site.css` |

---

## Usage Examples

### Basic local setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_portfolio
.\.venv\Scripts\python manage.py runserver
```

---

### Project archive

```text
http://127.0.0.1:8000/projects/
```

---

### Tag filter

```text
http://127.0.0.1:8000/projects/tag/operations/
```

---

### HTMX partial check

```bash
curl -H "HX-Request: true" http://127.0.0.1:8000/projects/
```

Expected:
- project grid partial
- no full site header

---

### Contact form HTMX success

Submit valid `name`, `email`, `message`, empty `referral_source`, and `HX-Request: true`.

Expected:
```text
Message received
```

---

### Intentional failure — invalid contact email

Submit:
```text
email=bad-email
```

Expected:
```text
Enter a valid email address
```

---

### Intentional failure — unpublished project

Requesting an unpublished project detail URL returns:
```text
404
```

---

## Public Python Interfaces

Important internal/public interfaces:
- `Project.objects.published()`
- `Project.objects.featured()`
- `Project.objects.by_tag(slug)`
- `Project.get_absolute_url()`
- `Project._build_unique_slug()`
- `get_featured_projects()`
- `get_adjacent_projects(project)`
- `ProjectListView`
- `ProjectDetailView`
- `ContactSubmissionForm`
- `contact.views.contact`
- `client_ip(request)`
- `markdownify`
- `reading_time`
- `active_nav`
- `canonical_urls`
- `seed_portfolio`

---

*Constitution reference: Article 4 (input/output boundaries), Article 6 (verification), and Article 8 (understandable and verifiable work).*

---


# Runbook
## App — Personal Portfolio Website
**Portfolio Platform Group | Document 4 of 5**

---

## Requirements

### Local development

- Python 3.12 target runtime
- pip
- Git
- SQLite through Django default local database URL
- Tailwind standalone binary only when rebuilding CSS
- pytest and pytest-django for tests

The README notes that the current machine used for local verification exposed Python 3.14 while the project target remains Python 3.12.

---

### Production

- Railway or equivalent host
- `DJANGO_SETTINGS_MODULE=portfolio_site.settings.prod`
- Gunicorn
- Postgres-compatible `DATABASE_URL`
- collected static files
- configured `SECRET_KEY`, `ALLOWED_HOSTS`, and `CANONICAL_URL`

---

## Installation Procedure

### Clone

```bash
git clone https://github.com/PrincetonAfeez/Personal-Portfolio-Website.git
cd Personal-Portfolio-Website
```

---

### Create virtual environment

PowerShell:

```powershell
python -m venv .venv
```

---

### Install dependencies

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
```

---

### Configure environment

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set local values.

Minimum useful local values:
```text
SECRET_KEY=<local-secret>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
CANONICAL_URL=http://127.0.0.1:8000
```

---

### Initialize database

```powershell
.\.venv\Scripts\python manage.py migrate
```

---

### Seed sample content

```powershell
.\.venv\Scripts\python manage.py seed_portfolio
```

This creates:
- sample projects
- sample tags
- sample tech-stack entries
- skills
- timeline entries
- generated project hero images
- generated static operations map
- generated static resume PDF

---

### Run development server

```powershell
.\.venv\Scripts\python manage.py runserver
```

Open:
```text
http://127.0.0.1:8000/
```

---

## Configuration Steps

### Development settings

Default:
```text
portfolio_site.settings.dev
```

Behavior:
- DEBUG true
- local allowed hosts
- WhiteNoise removed from middleware for development
- SQLite default from `DATABASE_URL`
- request timing header enabled

---

### Production settings

Set:
```text
DJANGO_SETTINGS_MODULE=portfolio_site.settings.prod
SECRET_KEY=<strong-secret>
DEBUG=False
ALLOWED_HOSTS=<production-hosts>
DATABASE_URL=<postgres-url>
CANONICAL_URL=<https-site-origin>
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

Optional contact email:
```text
CONTACT_NOTIFICATION_EMAIL=<owner-email>
EMAIL_BACKEND=<real-email-backend>
DEFAULT_FROM_EMAIL=<from-address>
```

---

## Running the App

### Development

```bash
python manage.py runserver
```

Healthy:
- home page returns 200
- `/projects/` returns 200
- `/about/` returns 200
- `/contact/` returns 200
- `/resume/` returns 200
- `/robots.txt` returns 200
- `/sitemap.xml` returns 200

---

### Production

Railway/Procfile:

```bash
python manage.py migrate &&
python manage.py collectstatic --noinput &&
gunicorn portfolio_site.wsgi:application --log-file -
```

Healthy:
- migrations complete
- static collection completes
- Gunicorn boots
- app responds on platform port

---

## Running Tests

```powershell
.\.venv\Scripts\python -m pytest
```

Verbose:

```powershell
.\.venv\Scripts\python -m pytest -vv --tb=short
```

Focused examples:

```bash
python -m pytest projects/tests.py
python -m pytest contact/tests.py
python -m pytest core/tests.py
```

---

## Rebuilding CSS

Use Tailwind standalone:

```powershell
tailwindcss -i .\assets\tailwind\input.css -o .\static\css\site.css --minify
```

Rebuild after:
- changing Tailwind source
- changing class usage if the standalone workflow requires refresh
- changing core layout styling assumptions

The compiled `static/css/site.css` is committed.

---

## Standard Operating Procedures

### Add a project manually through admin

1. Create tags and tech-stack entries as needed.
2. Create project with title, summary, body, status fields, and publication date.
3. Leave slug blank for automatic generation or set a manual slug.
4. Attach tags and tech stack.
5. Mark `is_published=True`.
6. Set `published_at` to current/past date.
7. Verify `/projects/` and project detail URL.

---

### Add sample/demo content

```bash
python manage.py seed_portfolio
```

This command is idempotent for named/titled records through `update_or_create()` patterns, but generated hero images are only added when missing.

---

### Check project publication rules

In shell:

```bash
python manage.py shell
```

```python
from projects.models import Project
Project.objects.published()
Project.objects.featured()
```

---

### Test HTMX project partials

```bash
curl -H "HX-Request: true" http://127.0.0.1:8000/projects/
```

Expected:
- partial HTML
- `project-grid-shell`
- no `site-header`
- no full doctype

---

### Test contact form

1. Visit `/contact/`.
2. Submit valid name, email, and message.
3. Confirm success message.
4. Confirm `ContactSubmission` row in admin or shell.

---

### Test rate limiting

Set low limit in local settings or test override, then post from the same IP until the form shows:
```text
Please wait a few minutes before sending another message.
```

---

### Test robots and sitemap

```text
/robots.txt
/sitemap.xml
```

Expected:
- robots includes canonical sitemap URL
- sitemap includes static routes and published projects

---

## Health Checks

### Home

```text
GET /
```

Healthy:
```text
200
```

---

### Project archive

```text
GET /projects/
```

Healthy:
- status 200
- project grid visible
- filters visible when tags exist

---

### Tag archive

```text
GET /projects/tag/operations/
```

Healthy:
- status 200 for existing tag
- status 404 for unknown tag

---

### Project detail

```text
GET /projects/<published-project-slug>/
```

Healthy:
- status 200
- project body rendered
- tags and adjacent navigation visible when present

---

### Contact

```text
GET /contact/
POST /contact/
```

Healthy:
- GET 200
- valid POST saves or redirects/returns success
- invalid POST shows errors
- honeypot does not save

---

### SEO routes

```text
GET /robots.txt
GET /sitemap.xml
```

Healthy:
- robots includes canonical sitemap URL
- sitemap includes static routes and published projects

---

### Static assets

Check browser Network tab:
- `/static/css/site.css` loads
- HTMX script loads from unpkg
- media/thumbnail images load when projects have images

---

## Expected Output Samples

### `seed_portfolio`

```text
Seeded portfolio content and images.
```

---

### robots.txt

```text
User-agent: *
Allow: /

Sitemap: http://127.0.0.1:8000/sitemap.xml
```

Production should use the configured canonical host.

---

### Contact success panel

```text
Message received
Thanks for reaching out. I’ll review it and follow up from the direct email channel.
```

---

### Rate-limit error

```text
Please wait a few minutes before sending another message.
```

---

### Test run

```text
pytest
```

Expected:
- all tests pass
- project/contact/core/about tests run

---

## Known Failure Modes

### `ModuleNotFoundError: No module named 'django'`

**Trigger:** dependencies not installed or virtual environment not active.

**Resolution:**
```bash
python -m pip install -r requirements-dev.txt
```

---

### Project archive is empty

**Trigger:** no projects seeded or no projects are published.

**Resolution:**
```bash
python manage.py seed_portfolio
```

Or verify:
- `is_published=True`
- `published_at` set
- `published_at <= now`

---

### Unpublished project returns 404

**Trigger:** project exists but does not satisfy `published()` queryset rules.

**Resolution:**
Set:
```text
is_published=True
published_at=<current or past datetime>
```

---

### HTMX partial returns full page

**Trigger:** missing or incorrect `HX-Request: true` header.

**Resolution:**
Confirm request header is exactly:
```text
HX-Request: true
```

---

### Contact form does not send email

**Trigger:** `CONTACT_NOTIFICATION_EMAIL` unset or email backend configured as console.

**Resolution:**
Set:
```text
CONTACT_NOTIFICATION_EMAIL=<recipient>
EMAIL_BACKEND=<real backend>
DEFAULT_FROM_EMAIL=<from address>
```

---

### Contact submissions blocked too soon

**Trigger:** low `CONTACT_RATE_LIMIT_MAX` or cache key reusing same client IP.

**Resolution:**
Review:
```text
CONTACT_RATE_LIMIT_WINDOW
CONTACT_RATE_LIMIT_MAX
HTTP_X_FORWARDED_FOR / REMOTE_ADDR handling
```

---

### Contact rate limiting ineffective across workers

**Trigger:** local memory cache is per-process.

**Resolution:**
Use a shared cache backend such as Redis if the site runs multiple worker processes and strict global rate limiting is required.

---

### Static files missing in production

**Trigger:** `collectstatic` not run, manifest mismatch, or missing source file.

**Resolution:**
```bash
python manage.py collectstatic --noinput
```

Check `STATIC_ROOT`, WhiteNoise, and referenced static file paths.

---

### HTTPS redirect issue

**Trigger:** production `SECURE_SSL_REDIRECT=True` without correct proxy/host configuration.

**Resolution:**
Confirm platform forwards scheme correctly and production host settings are valid.

---

### CSP blocks scripts/styles

**Trigger:** CSP does not match actual script/style sources.

**Resolution:**
Review `CONTENT_SECURITY_POLICY`, HTMX CDN usage, inline style/script needs, and static assets.

---

## Troubleshooting Decision Tree

```text
Site will not start
  ├── Missing dependencies?
  │     └── pip install -r requirements-dev.txt or requirements.txt
  ├── Settings module wrong?
  │     └── Use portfolio_site.settings.dev locally or prod in Railway
  ├── Database unavailable?
  │     └── Check DATABASE_URL and run migrate
  └── Static collection failure?
        └── Verify static paths and collectstatic

Projects page is wrong
  ├── No data?
  │     └── Run seed_portfolio
  ├── Draft/future content?
  │     └── Check is_published and published_at
  ├── HTMX issue?
  │     └── Check HX-Request header and htmx script loading
  └── Pagination issue?
        └── Validate page query parameter

Contact form issue
  ├── Invalid form data?
  │     └── Check field errors
  ├── Honeypot filled?
  │     └── Submission intentionally ignored
  ├── Rate limited?
  │     └── Wait or adjust rate-limit settings
  └── Email failed?
        └── Check EMAIL_BACKEND and logs

SEO issue
  ├── Wrong canonical URL?
  │     └── Set CANONICAL_URL
  ├── Sitemap missing projects?
  │     └── Confirm projects are published
  └── robots points to wrong host?
        └── Update CANONICAL_URL
```

---

## Dependency Failure Handling

### Python packages

```bash
python -m pip install -r requirements-dev.txt
```

For production:
```bash
python -m pip install -r requirements.txt
```

---

### Database

```bash
python manage.py migrate
```

If using production:
- confirm `DATABASE_URL`
- confirm Postgres service availability
- confirm psycopg installed

---

### Tailwind

Rebuild CSS with standalone binary:
```powershell
tailwindcss -i .\assets\tailwind\input.css -o .\static\css\site.css --minify
```

---

## Recovery Procedures

### Recover from broken local database

```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_portfolio
```

PowerShell:
```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed_portfolio
```

---

### Recover from missing seed assets

```bash
python manage.py seed_portfolio
```

This recreates:
- operations map
- resume PDF
- sample project hero images when missing

---

### Recover from contact spam/rate-limit cache during local testing

Restart server or clear cache through Django shell/test context. LocMem cache is process-local.

---

### Recover from broken CSS

Regenerate:
```powershell
tailwindcss -i .\assets\tailwind\input.css -o .\static\css\site.css --minify
```

Or restore committed CSS from git:
```bash
git checkout -- static/css/site.css
```

---

### Recover from production deploy failure

1. Check Railway deploy logs.
2. Identify whether failure occurred in:
   - migrate
   - collectstatic
   - Gunicorn boot
3. Reproduce locally with production settings when possible.
4. Fix environment/static/database issue.
5. Redeploy.

---

## Logging Reference

Logging is configured in `portfolio_site.settings.base`.

Format:
```text
%(asctime)s %(levelname)s %(name)s %(message)s
```

Handler:
```text
console
```

Root logger level:
```text
LOG_LEVEL environment variable, default INFO
```

Contact notification email failures are logged with:
```python
logger.exception("Contact notification email failed")
```

Request timing is not logged, but in DEBUG mode the response receives:
```text
X-Request-Duration-ms
```

---

## Maintenance Notes

- Keep `Project.objects.published()` as the single publication rule.
- Add tests when changing publication/filtering behavior.
- Keep contact form spam protections intact.
- Use a shared cache backend if rate limiting must work across workers.
- Consider vendoring HTMX to tighten CSP.
- Consider replacing `unsafe-inline` with nonces/hashes or stricter static-only styling.
- Consider a separate Railway release phase instead of running migrations/collectstatic in the start command.
- Keep `CANONICAL_URL` accurate for SEO.
- Rebuild `static/css/site.css` after Tailwind source changes.
- Keep generated seed content clearly identified as sample data.

---

*Constitution reference: Article 6 (behavior verification), Article 5 (constraints and trade-offs), and Article 8 (verifiable learner work).*

---


# Lessons Learned
## App — Personal Portfolio Website
**Portfolio Platform Group | Document 5 of 5**

---

## Why This Design Was Chosen

This design was chosen because a personal portfolio can be more than a static résumé. The project demonstrates a real Django system: models, querysets, class-based views, forms, middleware, context processors, template tags, markdown rendering, image generation, sitemaps, contact persistence, rate limiting, deployment settings, and tests.

The central architectural choice was to keep the application server-rendered. That decision matches the learning objective: Python, Django, HTMX, and operational software design. HTMX provides useful progressive enhancement without requiring a JavaScript framework or JSON API. The result is a site that remains understandable as a Django application from request to response.

The project catalogue is the strongest technical area. It uses publication-aware querysets, featured project services, tag filtering, adjacent-project navigation, and project sitemaps. This turns the portfolio from a list of cards into a content system.

---

## What Was Intentionally Omitted

**JavaScript framework:** No React, Vue, or SPA architecture is used. HTMX provides the needed interactivity.

**API layer:** The site does not expose a public JSON API. Views return HTML or partial HTML.

**Full CMS:** Content is managed through Django models/admin and a seed command, not a headless CMS.

**Complex deployment orchestration:** Railway plus Gunicorn is enough for the current scale.

**Dedicated task queue:** Contact email notification happens inline. There is no Celery/RQ/background worker.

**Shared production cache:** LocMem cache is enough for local/simple deployment, but not for strict multi-worker rate limiting.

**Strictest possible CSP:** The current implementation supports HTMX CDN and inline styles/scripts. A stricter CSP is a future hardening step.

---

## Biggest Weakness

The biggest weakness is that production hardening is incomplete compared with the strongest possible Django deployment. HTMX is loaded from a CDN, and the CSP permits `unsafe-inline`. That is acceptable for a learning portfolio, especially with SRI on the HTMX script, but it is not as strong as self-hosted scripts plus nonced or fully static scripts/styles.

The second weakness is contact rate limiting through LocMem cache. It works for a single process and is easy to test, but it is not global across multiple workers or instances. If the site receives real traffic or spam, the rate limit should move to Redis or another shared cache.

The third weakness is deployment sequencing. Running migrations and collectstatic in the start command is simple, but a larger production app would use a release phase or separate deploy step.

---

## Scaling Considerations

**If the project catalogue grows:**
- Add search.
- Add tech-stack filtering.
- Add date/status filtering.
- Add database indexes where needed.
- Add stronger pagination UX.

**If contact traffic increases:**
- Move rate limiting to Redis.
- Add CAPTCHA or a stronger bot-defense layer.
- Move notification email into a background task.
- Add admin workflow for reviewing submissions.

**If production hardening increases:**
- Vendor HTMX locally.
- Remove `unsafe-inline` from CSP.
- Add CSP nonces or hashes where needed.
- Add deployment health checks.
- Add structured JSON logging.

**If content management grows:**
- Replace sample seed command with manifest-driven content sync.
- Separate sample/demo data from production data.
- Add import/export validation.

**If media grows:**
- Move media storage to an object store.
- Add CDN-backed static/media serving.
- Add thumbnail cleanup and image validation workflows.

---

## What the Next Refactor Would Be

1. **Vendor HTMX locally** — remove the dependency on unpkg and tighten CSP.

2. **Replace LocMem rate limiting with a shared cache option** — make rate limiting correct across workers.

3. **Separate deployment release steps** — move migrations and collectstatic out of the long-running start command.

4. **Add manifest-driven project seeding** — replace hardcoded sample content with a version-controlled content manifest.

5. **Add a health endpoint** — support production uptime checks and deploy smoke tests.

6. **Add richer project documentation links** — connect project entries to the Core 5 documentation convention.

---

## What This Project Taught

- **Server-rendered Django can still feel interactive.** HTMX partials let the site update filtered project grids and contact forms without a frontend framework.

- **Querysets are business logic.** The `published()`, `featured()`, and `by_tag()` methods define what the public site is allowed to show. That is more maintainable than repeating filters in views.

- **Forms need abuse handling.** Honeypots, rate limits, IP recording, validation, and email failure handling are part of responsible contact-form design.

- **Markdown rendering needs sanitization.** The `markdownify` filter shows the right instinct: author-friendly Markdown must be cleaned before being trusted in templates.

- **Deployment choices shape architecture.** Railway, Gunicorn, WhiteNoise, environment variables, and Postgres-ready settings are part of the system, not afterthoughts.

- **Tests protect real behavior.** The tests do not just check status codes. They verify publication rules, slug collisions, HTMX partials, rate limiting, honeypots, canonical URLs, sitemap output, and custom error pages.

- **A portfolio should demonstrate judgment.** The project makes practical trade-offs: no SPA, no API, simple deployment, sample seeding, and focused Django architecture. Those choices are appropriate for the project’s size and learning goals.

---

*Constitution v2.0 checklist: This document satisfies Article 5 (trade-off documentation), Article 6 (verification), and Article 7 (progressive complexity) for the Personal Portfolio Website.*
