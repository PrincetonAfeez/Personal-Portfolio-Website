"""Admin configuration for the core app."""

from django.contrib import admin
from .models import Project, Tag, TechStack as TechStackAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "is_featured", "published_at", "updated_at")
    list_filter = ("is_published", "is_featured", "tags", "tech_stack")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    filter_horizontal = ("tags", "tech_stack")
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "body")}),
        ("Media", {"fields": ("hero_image", "hero_alt")}),
        ("Taxonomy", {"fields": ("tags", "tech_stack")}),
        ("Publishing", {"fields": ("is_published", "is_featured", "published_at")}),
        ("Links", {"fields": ("repo_url", "demo_url")}),
    )
