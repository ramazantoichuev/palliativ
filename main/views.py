from django.views.generic import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _

from common.notifications import notify_admins, send_confirmation
from .models.consultation import ConsultationRequest
from .forms import ConsultationForm

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

    def form_valid(self, form):
        response = super().form_valid(form)
        admin_url = self.request.build_absolute_uri(
            reverse('admin:main_consultationrequest_change', args=[self.object.pk])
        )
        notify_admins(
            'Новая заявка на консультацию',
            f'Имя: {self.object.first_name}\nТелефон: {self.object.phone}\n'
            f'Тема: {self.object.get_topic_display()}\nАдминка: {admin_url}',
        )
        send_confirmation(self.object.email, 'Заявка на консультацию принята', 'Ваша заявка принята, мы свяжемся с вами.')
        return response

