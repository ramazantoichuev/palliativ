import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.honeypot import HoneypotFormMixin
from common.turnstile_form import TurnstileFormMixin

from .models import Event, EventRegistration


def _normalize_phone(value):
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("0"):
        digits = "996" + digits[1:]
    return digits

class EventRegistrationForm(HoneypotFormMixin, TurnstileFormMixin, forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ["full_name", "email", "phone"]
        labels = {
            "email": _("Email (необязательно)"),
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        if self.event and phone:
            wanted = _normalize_phone(phone)
            existing = EventRegistration.objects.filter(
                event=self.event
            ).values_list("phone", flat=True)
            if any(_normalize_phone(p) == wanted for p in existing):
                self.add_error(
                    "phone",
                    ValidationError(_("Вы уже зарегистрированы на это мероприятие")),
                )
        return cleaned_data
    
class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "slug",
            "description",
            "content",
            "location",
            "image",
            "event_date",
        ]
        # SplitDateTimeWidget возвращает пару [дата, время] — ему обязателен
        # парный SplitDateTimeField, иначе DateTimeField падает на списке.
        field_classes = {"event_date": forms.SplitDateTimeField}
        widgets = {
            "event_date": forms.SplitDateTimeWidget(
                date_format="%Y-%m-%d",
                time_format="%H:%M",
                date_attrs={
                    "type": "date",
                    "class": "form-control d-inline-block",
                    "style": "width: 48%; margin-right: 2%; position: relative; z-index: 5;",
                },
                time_attrs={
                    "type": "time",
                    "class": "form-control d-inline-block",
                    "style": "width: 49%; position: relative; z-index: 5;",
                },
            ),
        }
