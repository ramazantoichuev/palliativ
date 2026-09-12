from common.notifications import notify_admins
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from .forms import (
    DoctorApplicationForm,
    EmailAuthenticationForm,
    PatientRegistrationForm,
)

User = get_user_model()


class PatientRegisterView(View):
    def get(self, request):
        form = PatientRegistrationForm()
        return render(request, "accounts/patient_register.html", {"form": form})

    def post(self, request):
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            admin_url = request.build_absolute_uri(reverse("admin:accounts_baseuser_change", args=[user.pk]))
            notify_admins("Новая регистрация пациента", f"Email: {user.email}\nАдминка: {admin_url}")
            return redirect("main:about")
        return render(request, "accounts/patient_register.html", {"form": form})

class DoctorRegisterView(View):
    def get(self, request):
        form = DoctorApplicationForm()
        return render(request, "accounts/doctor_register.html", {"form": form})

    def post(self, request):
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
