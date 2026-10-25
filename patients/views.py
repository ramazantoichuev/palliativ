from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from accounts.models import BaseUser

from .forms import SymptomSurveyForm
from .matching import match_for_cards
from .models import PatientCard


class DoctorPatientListView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = "patients/doctor_dashboard.html"
    context_object_name = "patient_cards"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != BaseUser.Role.DOCTOR:
            raise PermissionDenied(_("Доступ разрешен только врачам."))
        if not hasattr(request.user, "doctor_profile"):
            raise PermissionDenied(
                _("Ваш профиль врача еще не зарегистрирован в базе данных.")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        cards = list(
            PatientCard.objects.filter(doctor__user=self.request.user)
            .order_by("-updated_at")
            .select_related("patient__user", "doctor__user")
            .prefetch_related("symptoms")
        )
        return match_for_cards(cards)


class PatientCardDetailView(LoginRequiredMixin, ListView):
    model = PatientCard
    template_name = "patients/patient_dashboard.html"
    context_object_name = "patient_cards"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.role != BaseUser.Role.PATIENT:
            raise PermissionDenied(_("Доступ разрешен только пациентам."))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            PatientCard.objects.filter(patient__user=self.request.user)
            .order_by("-updated_at")
            .select_related("patient__user", "doctor__user")
            .prefetch_related("symptoms")
        )


class SymptomSurveyView(LoginRequiredMixin, View):
    template_name = "patients/symptom_survey.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.role != BaseUser.Role.PATIENT:
            raise PermissionDenied(_("Доступ разрешен только пациентам."))

        return super().dispatch(request, *args, **kwargs)

    def get_card(self):
        return (
            PatientCard.objects.filter(patient__user=self.request.user)
            .order_by("-updated_at")
            .first()
        )

    def get(self, request, *args, **kwargs):
        card = self.get_card()

        if card is None:
            messages.info(
                request,
                _("Карточка ещё не заведена — с вами свяжется сотрудник"),
            )
            return redirect("patients:patient_dashboard")

        form = SymptomSurveyForm(initial={"symptoms": card.symptoms.all()})
        return render(
            request,
            self.template_name,
            {"form": form},
        )

    def post(self, request, *args, **kwargs):
        card = self.get_card()

        if card is None:
            messages.info(
                request,
                _("Карточка ещё не заведена — с вами свяжется сотрудник"),
            )
            return redirect("patients:patient_dashboard")

        form = SymptomSurveyForm(request.POST)

        if form.is_valid():
            card.symptoms.set(form.cleaned_data["symptoms"])
            card.save(update_fields=["updated_at"])
            messages.success(
                request,
                _(
                    "Спасибо! Симптомы обновлены, ниже — материалы, которые могут помочь"
                ),
            )
            return redirect("patients:patient_dashboard")

        return render(
            request,
            self.template_name,
            {"form": form},
        )
