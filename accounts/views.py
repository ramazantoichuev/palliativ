from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views import View
from .forms import BaseUserCreationForm
User = get_user_model()

# class RegisterView(View):
#     def get(self, request):
#         form = BaseUserCreationForm
#         return render(request, 'accounts/register.html', {'form': form})
#
#     def post(self, request):
#         form = BaseUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             if user.role == user.Role.DOCTOR:
#                 profile = user.doctor_profile
#                 profile.education = form.cleaned_data['education']
#                 profile.skills = form.cleaned_data['skills']
#                 profile.save()
#             elif user.role == user.Role.PATIENT:
#                 profile = user.patient_profile
#                 profile.diagnosis = form.cleaned_data['diagnosis']
#                 profile.save()
#             return render(request, 'accounts/register.html', {'success': True})
#         return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()

        if user.role == User.Role.DOCTOR and not user.is_approved:
            return redirect('accounts:waiting_approval')
        return super().form_valid(form)

class WaitingApprovalView(TemplateView):
    template_name = 'accounts/waitig_403.html'

