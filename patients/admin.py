from django import forms
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import PatientCard, Symptom
from django.http import JsonResponse
from django.urls import path


class PatientCardAdminForm(forms.ModelForm):
    class Meta:
        model = PatientCard
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and self.data.get('patient'):
            try:
                from accounts.models import PatientProfile
                patient = PatientProfile.objects.get(pk=self.data.get('patient'))
                self.fields['diagnosis'].initial = patient.diagnosis
            except PatientProfile.DoesNotExist:
                pass

@admin.register(PatientCard)
class PatientCardAdmin(admin.ModelAdmin):
    form = PatientCardAdminForm
    list_display = ('patient', 'doctor', 'created_at', 'updated_at')
    autocomplete_fields = ['patient', 'doctor']
    filter_horizontal = ('symptoms',)

    class Media:
        js = ('patients/js/patient_diagnosis_autofill.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'get-patient-diagnosis/<int:patient_id>/',
                self.admin_site.admin_view(self.get_patient_diagnosis),
                name='patients_patientcard_get_diagnosis'
            ),
        ]
        return custom_urls + urls

    def get_patient_diagnosis(self, request, patient_id):
        from accounts.models import PatientProfile
        try:
            patient = PatientProfile.objects.get(pk=patient_id)
            return JsonResponse({'diagnosis': patient.diagnosis or ''})
        except PatientProfile.DoesNotExist:
            return JsonResponse({'diagnosis': ''})

@admin.register(Symptom)
class SymptomAdmin(TranslationAdmin):
    search_fields = ['name_ru', 'name_en', 'name_ky']
