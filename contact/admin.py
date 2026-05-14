"""Admin configuration for the contact app."""


from django.contrib import admin

from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "submitted_at", "ip_address")
    search_fields = ("name", "email", "message")
    readonly_fields = ("submitted_at", "ip_address")
    date_hierarchy = "submitted_at"

# Register your models here.
