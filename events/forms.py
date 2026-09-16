from django import forms

from .models import Event, EventRegistration


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ["full_name", "email", "phone"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "slug", "description","content", "location", "image", "event_date"]
        widgets = {
            'event_date': forms.SplitDateTimeWidget(
                date_format='%Y-%m-%d',
                time_format='%H:%M',
                date_attrs={
                    'type': 'date',
                    'class': 'form-control d-inline-block',
                    'style': 'width: 48%; margin-right: 2%; position: relative; z-index: 5;'
                },
                time_attrs={
                    'type': 'time',
                    'class': 'form-control d-inline-block',
                    'style': 'width: 49%; position: relative; z-index: 5;'
                }
            ),
        }