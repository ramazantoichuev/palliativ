from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from .forms import ConsultationForm
from .models.consultation import ConsultationRequest


class HomeView(TemplateView):
    template_name = 'main/home.html'


class AboutView(TemplateView):
    template_name = 'main/about.html'


class ContactsView(TemplateView):
    template_name = 'main/contacts.html'


# Create your views here.

class ConsultationCreateView(SuccessMessageMixin, CreateView):
    model = ConsultationRequest
    form_class = ConsultationForm
    template_name = 'main/consultation.html'
    success_url = reverse_lazy('main:home')
    success_message = _("Ваша заявка на консультацию успешно отправлена!")
