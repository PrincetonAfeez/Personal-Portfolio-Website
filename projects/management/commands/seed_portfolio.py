"""Management command to seed the portfolio with sample content."""

from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from about.models import Skill, TimelineEntry
from projects.models import Project, Tag, TechStack


def image_bytes(title: str, accent: tuple[int, int, int]) -> bytes:
    width, height = 1200, 900
    image = Image.new("RGB", (width, height), (246, 249, 246))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.rectangle((0, 0, width, 210), fill=(25, 35, 33))
    draw.text((64, 68), title.upper(), fill=(255, 255, 255), font=font)
    draw.text((64, 116), "Hospitality operations system", fill=(220, 231, 225), font=font)

    for index, y in enumerate((280, 405, 530, 655)):
        shade = 255 - index * 10
        draw.rounded_rectangle((64, y, 1080, y + 82), radius=18, fill=(shade, shade, shade), outline=(216, 225, 219))
        draw.rounded_rectangle((92, y + 22, 220, y + 60), radius=12, fill=accent)
        draw.rectangle((260, y + 27, 760, y + 36), fill=(190, 205, 197))
        draw.rectangle((260, y + 50, 910, y + 59), fill=(223, 229, 225))

    for index, x in enumerate((810, 900, 990)):
        bar_height = 120 + index * 46
        draw.rounded_rectangle((x, 740 - bar_height, x + 48, 740), radius=10, fill=accent)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def write_static_hero() -> None:
    path = settings.BASE_DIR / "static" / "img" / "operations-map.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 960
    image = Image.new("RGB", (width, height), (30, 48, 43))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for y in range(0, height, 80):
        draw.line((0, y, width, y), fill=(43, 70, 63), width=1)
    for x in range(0, width, 100):
        draw.line((x, 0, x, height), fill=(43, 70, 63), width=1)

    cards = [
        (120, 120, 520, 280, (255, 255, 255), "Shift readiness"),
        (640, 190, 1120, 390, (235, 248, 240), "Inventory variance"),
        (260, 470, 760, 700, (255, 246, 229), "Guest recovery queue"),
        (940, 540, 1430, 770, (231, 246, 249), "Manager handoff"),
    ]
    for left, top, right, bottom, color, label in cards:
        draw.rounded_rectangle((left, top, right, bottom), radius=20, fill=color, outline=(198, 215, 207), width=2)
        draw.text((left + 30, top + 28), label.upper(), fill=(28, 77, 59), font=font)
        for row in range(3):
            y = top + 78 + row * 36
            draw.rounded_rectangle((left + 30, y, right - 34, y + 14), radius=7, fill=(199, 214, 207))
        draw.rounded_rectangle((right - 110, top + 24, right - 34, top + 58), radius=12, fill=(208, 91, 70))

    image.save(path)


def write_resume_pdf() -> None:
    path = settings.BASE_DIR / "static" / "resume" / "prince-anumudu-resume.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (850, 1100), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    lines = [
        "Prince Anumudu",
        "Hospitality Operations | Hospitality Technology",
        "",
        "Profile",
        "Hospitality professional building Python and Django systems for",
        "service workflows, manager handoffs, and operational visibility.",
        "",
        "Technical Focus",
        "Python, Django, HTMX, SQL modeling, pytest, deployment, systems architecture.",
        "",
        "Domain Strength",
        "Service operations, shift coordination, guest recovery, training workflows.",
        "",
        "Selected Projects",
        "Shift Handoff Board, Inventory Variance Tracker, Guest Recovery Queue.",
        "",
        "Contact",
        "hello@example.com | github.com | linkedin.com",
    ]
    y = 90
    for line in lines:
        draw.text((80, y), line, fill=(23, 33, 31), font=font)
        y += 38 if line else 24

    image.save(path, "PDF", resolution=100.0)


class Command(BaseCommand):
    help = "Seed the portfolio with sample hospitality-tech content."

    def handle(self, *args, **options):
        write_static_hero()
        write_resume_pdf()

        tag_data = [
            ("Operations", "Systems that reduce handoff friction."),
            ("Django", "Server-rendered Django applications."),
            ("HTMX", "Small interactions without a JavaScript framework."),
            ("Data Modeling", "Relational structures for business rules."),
            ("Service Design", "Interfaces tuned for guest-facing teams."),
            ("Automation", "Repeatable workflows with fewer manual steps."),
        ]
        tags = {
            slugify(name): Tag.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": description},
            )[0]
            for name, description in tag_data
        }

        tech_data = [
            ("Python", "language"),
            ("Django", "framework"),
            ("HTMX", "framework"),
            ("SQLite", "service"),
            ("PostgreSQL", "service"),
            ("Tailwind CSS", "tool"),
            ("pytest", "tool"),
            ("Railway", "service"),
        ]
        tech = {
            slugify(name): TechStack.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "category": category},
            )[0]
            for name, category in tech_data
        }

        skills = [
            ("Python", "Language", 12, 4),
            ("Django", "Framework", 10, 4),
            ("HTMX", "Frontend", 8, 4),
            ("SQL modeling", "Data", 9, 4),
            ("pytest", "Testing", 7, 3),
            ("Deployment", "Operations", 6, 3),
            ("Hospitality ops", "Domain", 48, 5),
            ("Systems architecture", "Architecture", 8, 3),
        ]
        for name, category, months, proficiency in skills:
            Skill.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "months_of_use": months,
                    "proficiency": proficiency,
                },
            )

        timeline = [
            (date(2025, 5, 1), "Started Python systems practice", "Focused on control flow, data structures, and command-line tools.", "learning"),
            (date(2025, 8, 1), "Moved into Django monoliths", "Built CRUD workflows with relational models and server-rendered templates.", "learning"),
            (date(2025, 11, 1), "Added HTMX interaction patterns", "Practiced partial swaps, form validation, and progressive enhancement.", "project"),
            (date(2026, 2, 1), "Designed hospitality operating models", "Mapped real service workflows into tags, states, and manager handoffs.", "work"),
            (date(2026, 5, 1), "Portfolio architecture pass", "Pulled learning into a deployable Django site with tests and seed data.", "project"),
        ]
        for entry_date, title, description, entry_type in timeline:
            TimelineEntry.objects.update_or_create(
                date=entry_date,
                title=title,
                defaults={"description": description, "entry_type": entry_type},
            )

        now = timezone.now()
        projects = [
            {
                "title": "Shift Handoff Board",
                "summary": "A manager-facing board that keeps open tasks, guest notes, and escalation states visible between shifts.",
                "tags": ["operations", "django", "htmx"],
                "tech": ["python", "django", "htmx", "sqlite", "pytest"],
                "accent": (27, 107, 120),
                "featured": True,
            },
            {
                "title": "Inventory Variance Tracker",
                "summary": "A lightweight variance log for comparing expected stock against service-period reality.",
                "tags": ["data-modeling", "operations", "automation"],
                "tech": ["python", "django", "postgresql", "pytest"],
                "accent": (214, 164, 68),
                "featured": True,
            },
            {
                "title": "Guest Recovery Queue",
                "summary": "A service recovery workflow that captures context, follow-up ownership, and resolution timing.",
                "tags": ["service-design", "htmx", "django"],
                "tech": ["python", "django", "htmx", "tailwind-css"],
                "accent": (208, 91, 70),
                "featured": True,
            },
            {
                "title": "Menu Change Checklist",
                "summary": "A structured launch checklist for menu updates, station prep, training notes, and day-one observations.",
                "tags": ["operations", "automation"],
                "tech": ["python", "django", "sqlite"],
                "accent": (24, 77, 59),
                "featured": False,
            },
            {
                "title": "Reservation Load Forecast",
                "summary": "A small forecasting practice project that turns cover counts into staffing and prep signals.",
                "tags": ["data-modeling", "automation"],
                "tech": ["python", "postgresql", "pytest"],
                "accent": (75, 95, 154),
                "featured": False,
            },
            {
                "title": "Training Progress Matrix",
                "summary": "A skills matrix for tracking cross-training, station confidence, and next coaching moments.",
                "tags": ["service-design", "django"],
                "tech": ["python", "django", "tailwind-css"],
                "accent": (27, 107, 120),
                "featured": False,
            },
            {
                "title": "Manager Daily Brief",
                "summary": "A daily snapshot combining shift notes, open issues, and priority follow-ups in one page.",
                "tags": ["htmx", "operations", "automation"],
                "tech": ["python", "django", "htmx", "railway"],
                "accent": (208, 91, 70),
                "featured": False,
            },
        ]

        for index, data in enumerate(projects):
            project, _created = Project.objects.update_or_create(
                title=data["title"],
                defaults={
                    "summary": data["summary"],
                    "body": self.project_body(data["title"]),
                    "hero_alt": f"Interface preview for {data['title']}",
                    "is_published": True,
                    "is_featured": data["featured"],
                    "published_at": now - timedelta(days=index * 17),
                    "repo_url": "https://github.com/",
                    "demo_url": "",
                },
            )
            project.tags.set(tags[tag_slug] for tag_slug in data["tags"])
            project.tech_stack.set(tech[tech_slug] for tech_slug in data["tech"])

            if not project.hero_image:
                filename = f"{slugify(project.title)}.png"
                project.hero_image.save(
                    filename,
                    ContentFile(image_bytes(project.title, data["accent"])),
                    save=True,
                )

        self.stdout.write(self.style.SUCCESS("Seeded portfolio content and images."))

    @staticmethod
    def project_body(title: str) -> str:
        return f"""
## Problem

{title} explores a common hospitality coordination problem: useful context gets scattered across conversation, memory, and tools that were not designed for the pace of service.

## Approach

The project keeps the architecture intentionally small: Django models hold the durable business state, server-rendered templates keep the interface fast, and HTMX handles targeted updates without introducing an API layer.

## System notes

- Published records are filtered through manager methods.
- The interface favors direct scan paths over decorative chrome.
- Tests focus on query behavior, routing, and workflow regressions.

## What it demonstrates

This build connects hospitality judgment with software structure. It treats operational nuance as a modeling problem, then turns that model into a clear, maintainable user experience.
""".strip()
