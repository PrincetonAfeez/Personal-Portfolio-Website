"""Admin configuration for the about app."""

from django.contrib import admin

from .models import Skill, TimelineEntry


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "months_of_use", "proficiency")
    list_filter = ("category", "proficiency")
    search_fields = ("name", "category")


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "title", "entry_type")
    list_filter = ("entry_type",)
    search_fields = ("title", "description")
    date_hierarchy = "date"

# Register your models here.
