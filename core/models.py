"""Models for the core app."""

from django.db import models

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