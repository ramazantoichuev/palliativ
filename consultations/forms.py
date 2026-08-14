from django import forms
from .models import ConsultationRequest


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['first_name', 'phone', 'email', 'topic']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
        }