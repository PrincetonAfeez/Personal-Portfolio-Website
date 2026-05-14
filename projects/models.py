"""Models for the projects app."""

from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class ProjectQuerySet(models.QuerySet):
    def published(self) -> "ProjectQuerySet":
        return self.filter(
            is_published=True,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        ).order_by("-published_at", "-created_at")

    def featured(self) -> "ProjectQuerySet":
        return self.published().filter(is_featured=True)

    def by_tag(self, slug: str) -> "ProjectQuerySet":
        return self.published().filter(tags__slug=slug).distinct()


class ProjectManager(models.Manager.from_queryset(ProjectQuerySet)):
    pass


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TechStack(models.Model):
    class Category(models.TextChoices):
        LANGUAGE = "language", "Language"
        FRAMEWORK = "framework", "Framework"
        TOOL = "tool", "Tool"
        SERVICE = "service", "Service"

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "tech stack item"
        verbose_name_plural = "tech stack"

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.TextField(help_text="Short copy used on cards and meta descriptions.")
    body = models.TextField(help_text="Markdown writeup rendered server-side.")
    hero_image = models.ImageField(upload_to="projects/heroes/", blank=True)
    hero_alt = models.CharField(max_length=200, blank=True)
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    tech_stack = models.ManyToManyField(TechStack, related_name="projects", blank=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    repo_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("projects:detail", kwargs={"slug": self.slug})

    def _build_unique_slug(self) -> str:
        base_slug = slugify(self.title) or "project"
        slug = base_slug[:190]
        suffix = 2

        while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix_text = f"-{suffix}"
            slug = f"{base_slug[: 200 - len(suffix_text)]}{suffix_text}"
            suffix += 1

        return slug