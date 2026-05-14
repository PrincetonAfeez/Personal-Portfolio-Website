"""Models for the about app."""

from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=80)
    months_of_use = models.PositiveSmallIntegerField(default=0)
    proficiency = models.PositiveSmallIntegerField(default=3)

    class Meta:
        ordering = ["category", "-proficiency", "name"]

    def __str__(self) -> str:
        return self.name


class TimelineEntry(models.Model):
    class EntryType(models.TextChoices):
        LEARNING = "learning", "Learning"
        WORK = "work", "Work"
        PROJECT = "project", "Project"

    date = models.DateField()
    title = models.CharField(max_length=140)
    description = models.TextField()
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "timeline entries"

    def __str__(self) -> str:
        return self.title

