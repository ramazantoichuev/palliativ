from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from common.notifications import notify_admins
from main.models.system_settings import SystemSettings

from .forms import (
    DoctorApplicationForm,
    EmailAuthenticationForm,
    PatientRegistrationForm,
)

User = get_user_model()
class RegistrationGateMixin:
    settings_flag_name: str
    disabled_message: str
    disabled_template = "accounts/registration_disabled.html"

    def registration_enabled(self):
        return getattr(SystemSettings.load(), self.settings_flag_name)

    def render_disabled(self, request):
        return render(request, self.disabled_template, {"message": self.disabled_message})

class PatientRegisterView(RegistrationGateMixin, View):
    settings_flag_name = "patient_registration_enabled"
    disabled_message = _("Регистрация пациентов временно приостановлена. Попробуйте позже.")

    def get(self, request):
        if not self.registration_enabled():
            return self.render_disabled(request)
        form = PatientRegistrationForm()
        return render(request, "accounts/patient_register.html", {"form": form})

    def post(self, request):
        if not self.registration_enabled():
            return self.render_disabled(request)
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            admin_url = request.build_absolute_uri(reverse("admin:accounts_baseuser_change", args=[user.pk]))
            notify_admins("Новая регистрация пациента", f"Email: {user.email}\nАдминка: {admin_url}")
            return redirect("main:about")
        return render(request, "accounts/patient_register.html", {"form": form})

class DoctorRegisterView(RegistrationGateMixin, View):
    settings_flag_name = "doctor_registration_enabled"
    disabled_message = _("Регистрация врачей временно приостановлена. Попробуйте позже.")

    def get(self, request):
        if not self.registration_enabled():
            return self.render_disabled(request)
        form = DoctorApplicationForm()
        return render(request, "accounts/doctor_register.html", {"form": form})

    def post(self, request):
        if not self.registration_enabled():
            return self.render_disabled(request)
        form = DoctorApplicationForm(request.POST)
        if form.is_valid():
            user = form.save()
            admin_url = request.build_absolute_uri(reverse("admin:accounts_baseuser_change", args=[user.pk]))
            notify_admins("Новая заявка врача/волонтёра", f"Email: {user.email}\nАдминка: {admin_url}")
            return render(request, "accounts/doctor_application_sent.html")
        return render(request, "accounts/doctor_register.html", {"form": form})

class CustomLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        user = form.get_user()

        if user.role == User.Role.DOCTOR and not user.is_approved:
            return redirect("accounts:waiting_approval")

        return super().form_valid(form)


class WaitingApprovalView(TemplateView):
    template_name = "accounts/waiting_403.html"


class RegisterTypeView(TemplateView):
    template_name = "accounts/register_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_obj = SystemSettings.load()
        context["patient_registration_enabled"] = settings_obj.patient_registration_enabled
        context["doctor_registration_enabled"] = settings_obj.doctor_registration_enabled
        context["both_registrations_disabled"] = not (
            settings_obj.patient_registration_enabled or settings_obj.doctor_registration_enabled
        )
        return context
