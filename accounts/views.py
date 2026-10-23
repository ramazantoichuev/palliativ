from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from common.honeypot import honeypot_filled
from common.notifications import notify_admins
from common.ratelimit import (
    RATE_LIMIT_MESSAGE,
    check_rate_limit,
    is_limited,
    register_hit,
)
from common.utils import get_client_ip
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

    def render_rate_limited(self, request, template):
        messages.error(request, RATE_LIMIT_MESSAGE)
        return render(request, template, {"form": self.form_class()}, status=429)

    def render_disabled(self, request):
        return render(request, self.disabled_template, {"message": self.disabled_message})

class PatientRegisterView(RegistrationGateMixin, View):
    form_class = PatientRegistrationForm
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
        if honeypot_filled(request):
            return redirect("main:about")
        if not check_rate_limit(request, "patient_register"):
            return self.render_rate_limited(request, "accounts/patient_register.html")
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            admin_url = request.build_absolute_uri(reverse("admin:accounts_baseuser_change", args=[user.pk]))
            notify_admins(
                _("Новая регистрация пациента"),
                _("Email: {email}\nАдминка: {url}").format(
                    email=user.email,
                    url=admin_url
                )
            )
            return redirect("main:about")
        return render(request, "accounts/patient_register.html", {"form": form})

class DoctorRegisterView(RegistrationGateMixin, View):
    form_class = DoctorApplicationForm
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
        if honeypot_filled(request):
            return redirect("main:about")
        if not check_rate_limit(request, "patient_register"):
            return self.render_rate_limited(request, "accounts/patient_register.html")
        form = DoctorApplicationForm(request.POST)
        if form.is_valid():
            user = form.save()
            admin_url = request.build_absolute_uri(reverse("admin:accounts_baseuser_change", args=[user.pk]))
            notify_admins(
                _("Новая заявка врача/волонтёра"),
                _("Email: {email}\nАдминка: {url}").format(
                    email=user.email,
                    url=admin_url
                )
            )
            return render(request, "accounts/doctor_application_sent.html")
        return render(request, "accounts/doctor_register.html", {"form": form})

class CustomLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = "accounts/login.html"
    
    def post(self, request, *args, **kwargs):
        limit, _window = settings.RATE_LIMITS["login"]
        if is_limited("login", get_client_ip(request), limit):
            messages.error(request, RATE_LIMIT_MESSAGE)
            form = self.get_form_class()(request=request)
            context = self.get_context_data(form=form)
            return self.render_to_response(context, status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        _limit, window = settings.RATE_LIMITS["login"]
        register_hit("login", get_client_ip(self.request), window)
        return super().form_invalid(form)

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
