from django import forms

from .models import Symptom


class SymptomSurveyForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )