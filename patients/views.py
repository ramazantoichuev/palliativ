from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from accounts.models import BaseUser
from resources.models.resources import Resource

from .forms import SymptomSurveyForm
from .models import PatientCard

class DoctorPatientListView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = 'patients/doctor_dashboard.html'
    context_object_name = 'patient_cards'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != BaseUser.Role.DOCTOR:
            raise PermissionDenied("Доступ разрешен только врачам.")
        if not hasattr(request.user, 'doctor_profile'):
            raise PermissionDenied("Ваш профиль врача еще не зарегистрирован в базе данных.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        cards_list = list(
            PatientCard.objects.filter(doctor__user=self.request.user)
            .order_by('-updated_at')
            .select_related(
                'patient__user',
                'doctor__user'
            )
            .prefetch_related('symptoms')
        )
        all_symptom_ids = set()
        for card in cards_list:
            for symptom in card.symptoms.all():
                all_symptom_ids.add(symptom.id)
        if not all_symptom_ids:
            for card in cards_list:
                card._prefetched_matching_resources = []
            return cards_list

        resources = (
            Resource.objects
            .filter(symptoms__id__in=all_symptom_ids)
            .distinct()
            .prefetch_related('symptoms')
        )

        symptom_to_resources = {}
        for resource in resources:
            for symptom in resource.symptoms.all():
                if symptom.id not in symptom_to_resources:
                    symptom_to_resources[symptom.id] = []
                symptom_to_resources[symptom.id].append(resource)

        for card in cards_list:
            card_resources = set()
            for symptom in card.symptoms.all():
                if symptom.id in symptom_to_resources:
                    card_resources.update(symptom_to_resources[symptom.id])
            card._prefetched_matching_resources = list(card_resources)

        return cards_list


class PatientCardDetailView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = 'patients/patient_dashboard.html'
    context_object_name = 'patient_cards'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != BaseUser.Role.PATIENT:
            raise PermissionDenied("Доступ разрешен только пациентам.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            PatientCard.objects
            .filter(patient__user=self.request.user)
            .order_by('-updated_at')
            .select_related('patient__user', 'doctor__user')
            .prefetch_related('symptoms')
        )

class SymptomSurveyView(LoginRequiredMixin, View):
    template_name = 'patients/symptom_survey.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != BaseUser.Role.PATIENT:
            raise PermissionDenied("Доступ разрешен только пациентам.")
        return super().dispatch(request, *args, **kwargs)

    def get_card(self):
        return (
            PatientCard.objects
            .filter(patient__user=self.request.user)
            .order_by('-updated_at')
            .first()
        )

    def get(self, request, *args, **kwargs):
        card = self.get_card()

        if card is None:
            messages.info(
                request,
                "Карточка ещё не заведена — с вами свяжется сотрудник",
            )
            return redirect('patients:patient_dashboard')

        form = SymptomSurveyForm(
            initial={'symptoms': card.symptoms.all()}
        )
        return render(
            request,
            self.template_name,
            {'form': form},
        )

    def post(self, request, *args, **kwargs):
        card = self.get_card()

        if card is None:
            messages.info(
                request,
                "Карточка ещё не заведена — с вами свяжется сотрудник",
            )
            return redirect('patients:patient_dashboard')

        form = SymptomSurveyForm(request.POST)

        if form.is_valid():
            card.symptoms.set(form.cleaned_data['symptoms'])
            card.save(update_fields=['updated_at'])
            messages.success(
                request,
                "Спасибо! Симптомы обновлены, ниже — материалы, которые могут помочь",
            )
            return redirect('patients:patient_dashboard')

        return render(
            request,
            self.template_name,
            {'form': form},
        )
