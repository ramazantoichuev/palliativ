from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from common.honeypot import honeypot_filled
from common.notifications import notify_admins, send_confirmation
from common.ratelimit import RATE_LIMIT_MESSAGE, check_rate_limit
from events.models import Event
from news.models.posts import Post
from resources.models.resources import Resource

from .forms import ConsultationForm
from .models.consultation import ConsultationRequest
from .models.team import TeamMember


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

class SearchResultsView(TemplateView):
    template_name = "main/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("q", "").strip()
        context["query"] = search_query
        context["news_results"] = Post.objects.none()
        context["event_results"] = Event.objects.none()
        context["resource_results"] = Resource.objects.none()
        context["search_allowed"] = len(search_query) >= 2

        if context["search_allowed"]:
            news_query = Q()
            event_query = Q()
            resource_query = Q()

            for language_code, _ in settings.LANGUAGES:
                news_query |= Q(
                    **{f"title_{language_code}__icontains": search_query}
                )
                news_query |= Q(
                    **{f"description_{language_code}__icontains": search_query}
                )

                event_query |= Q(
                    **{f"title_{language_code}__icontains": search_query}
                )
                event_query |= Q(
                    **{f"description_{language_code}__icontains": search_query}
                )

                resource_query |= Q(
                    **{f"title_{language_code}__icontains": search_query}
                )
                resource_query |= Q(
                    **{f"description_{language_code}__icontains": search_query}
                )

            context["news_results"] = Post.objects.filter(news_query)
            context["event_results"] = Event.objects.filter(event_query)
            context["resource_results"] = Resource.objects.filter(resource_query)

        return context


class TeamView(TemplateView):
    template_name = "main/team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = TeamMember.objects.all()
        context["team_groups"] = [
            (label, [m for m in members if m.category == value])
            for value, label in TeamMember.Category.choices
        ]
        return context

# Create your views here.
class ConsultationCreateView(SuccessMessageMixin, CreateView):
    model = ConsultationRequest
    form_class = ConsultationForm
    template_name = "main/consultation.html"
    success_url = reverse_lazy("main:home")
    success_message = _("Ваша заявка на консультацию успешно отправлена!")

    def post(self, request, *args, **kwargs):
        if honeypot_filled(request):
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        if not check_rate_limit(request, "consultation"):
            self.object = None
            messages.error(request, RATE_LIMIT_MESSAGE)
            context = self.get_context_data(form=self.form_class())
            return self.render_to_response(context, status=429)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        since = timezone.now() - timedelta(
            seconds=settings.CONSULTATION_DUPLICATE_WINDOW
        )
        is_duplicate = ConsultationRequest.objects.filter(
            phone=form.cleaned_data["phone"],
            topic=form.cleaned_data["topic"],
            created_at__gte=since,
        ).exists()
        if is_duplicate:
            messages.success(self.request, self.success_message)
            return redirect(self.success_url)

        response = super().form_valid(form)
        admin_url = self.request.build_absolute_uri(
            reverse('admin:main_consultationrequest_change', args=[self.object.pk])
        )
        notify_admins(
            _('Новая заявка на консультацию'),
            _(
                'Имя: {first_name}\n'
                'Телефон: {phone}\n'
                'Тема: {topic}\n'
                'Админка: {url}'
            ).format(
                first_name=self.object.first_name,
                phone=self.object.phone,
                topic=self.object.get_topic_display(),
                url=admin_url
            ),
        )
        send_confirmation(
            self.object.email,
            _('Заявка на консультацию принята'),
            _('Ваша заявка принята, мы свяжемся с вами.'),
        )
        return response

