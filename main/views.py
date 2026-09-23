from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from common.notifications import notify_admins, send_confirmation
from events.models import Event
from news.models.posts import Post

from .forms import ConsultationForm
from .models.consultation import ConsultationRequest


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_posts"] = Post.objects.order_by("-created_at")[:3]
        context["upcoming_events"] = Event.objects.filter(
            event_date__gte=timezone.now()
        ).order_by("event_date")[:3]
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"


class ContactsView(TemplateView):
    template_name = "main/contacts.html"


class PrivacyPolicyView(TemplateView):
    template_name = "main/privacy_policy.html"


class ConsultationCreateView(SuccessMessageMixin, CreateView):
    model = ConsultationRequest
    form_class = ConsultationForm
    template_name = "main/consultation.html"
    success_url = reverse_lazy("main:home")
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