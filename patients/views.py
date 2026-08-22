from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from accounts.models import BaseUser
from .models import PatientCard


class DoctorPatientListView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = 'patients/doctor_dashboard.html'
    context_object_name = 'patient_cards'

    def dispatch(self, request, *args, **kwargs):
        # 1. Проверяем текстовую роль пользователя
        if request.user.role != BaseUser.Role.DOCTOR:
            raise PermissionDenied("Доступ разрешен только врачам.")

        # 2. Проверяем, существует ли у него doctor_profile в БД
        if not hasattr(request.user, 'doctor_profile'):
            raise PermissionDenied("Ваш профиль врача еще не зарегистрирован в базе данных.")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Теперь здесь обращаться к doctor_profile абсолютно безопасно
        return PatientCard.objects.filter(doctor=self.request.user.doctor_profile)
