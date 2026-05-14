"""Forms for the contact app."""

from django import forms

from .models import ContactSubmission


class ContactSubmissionForm(forms.ModelForm):
    referral_source = forms.CharField(
        required=False,
        strip=True,
        label="Company website",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
            }
        ),
    )

    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "message": forms.Textarea(attrs={"placeholder": "Tell me what you are building", "rows": 6}),
        }
