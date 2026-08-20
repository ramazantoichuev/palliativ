from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views import View
User = get_user_model()


from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from .forms import DoctorApplicationForm, PatientRegistrationForm, EmailAuthenticationForm


class PatientRegisterView(View):
    def get(self, request):
        form = PatientRegistrationForm()
        return render(request, 'accounts/patient_register.html', {'form': form})

    def post(self, request):
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:about')
        return render(request, 'accounts/patient_register.html', {'form': form})


class DoctorRegisterView(View):
    def get(self, request):
        form = DoctorApplicationForm()
        return render(request, 'accounts/doctor_register.html', {'form': form})

    def post(self, request):
        form = DoctorApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/doctor_application_sent.html')
        return render(request, 'accounts/doctor_register.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()

        if user.role == User.Role.DOCTOR and not user.is_approved:
            return redirect('accounts:waiting_approval')

        return super().form_valid(form)

class WaitingApprovalView(TemplateView):
    template_name = 'accounts/waiting_403.html'



