from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from accounts.models import BaseUser
from .models import PatientCard


class DoctorPatientListView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = 'patients/doctor_dashboard.html'
    context_object_name = 'patient_cards'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        if request.user.role != BaseUser.Role.DOCTOR:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return PatientCard.objects.filter(doctor=self.request.user.doctor_profile)


class PatientCardDetailView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = 'patients/patient_dashboard.html'
    context_object_name = 'patient_cards'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        if request.user.role != BaseUser.Role.PATIENT:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return PatientCard.objects.filter(
            patient=self.request.user.patient_profile
        ).order_by('-updated_at')