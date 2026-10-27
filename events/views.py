from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import FormMixin

from accounts.models import BaseUser
from common.honeypot import honeypot_filled
from common.notifications import notify_admins, send_confirmation
from common.ratelimit import RATE_LIMIT_MESSAGE, check_rate_limit

from .forms import EventRegistrationForm
from .models import Event


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ только для admin и moderator"""

    def test_func(self):
        return self.request.user.role in [BaseUser.Role.ADMIN, BaseUser.Role.MODERATOR]


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_context_data(self, **kwargs):
        from django.utils import timezone

        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["upcoming_events"] = Event.objects.filter(event_date__gte=now).order_by(
            "event_date"
        )
        context["past_events"] = Event.objects.filter(event_date__lt=now).order_by(
            "-event_date"
        )
        return context


class EventDetailView(SuccessMessageMixin, FormMixin, DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    form_class = EventRegistrationForm
    # Сообщение добавляется в form_valid, поэтому при невалидной форме
    # и прошедшем мероприятии (form_invalid) его не будет.
    success_message = gettext_lazy("Вы успешно зарегистрированы на мероприятие!")

    def get_success_url(self):
        return reverse("events:event_detail", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_past"] = self.object.is_past
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.object
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if honeypot_filled(request):
            # Как у консультации: бот видит тот же ответ, что и настоящий успех
            messages.success(request, self.success_message)
            return redirect(self.get_success_url())

        form = self.get_form()

        if self.object.is_past:
            form.add_error(None, _("Регистрация на это мероприятие закрыта"))
            return self.form_invalid(form)

        if not check_rate_limit(request, "event_registration"):
            messages.error(request, RATE_LIMIT_MESSAGE)
            form = self.form_class(event=self.object)
            context = self.get_context_data(form=form)
            return self.render_to_response(context, status=429)

        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = self.object
            registration.save()
            admin_url = request.build_absolute_uri(
                reverse(
                    "admin:events_eventregistration_change",
                    args=[registration.pk],
                )
            )
            notify_admins(
                _("Новая регистрация на мероприятие"),
                _("Событие: {title}\nАдминка: {url}").format(
                    title=self.object.title,
                    url=admin_url,
                ),
            )
            if registration.email:
                send_confirmation(
                    registration.email,
                    _("Регистрация на мероприятие принята"),
                    _("Вы зарегистрированы на «{title}».").format(
                        title=self.object.title
                    ),
                )
            return self.form_valid(form)

        return self.form_invalid(form)


class EventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    fields = ["title", "description", "image", "event_date", "location"]
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)


class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    fields = ["title", "description", "image", "event_date", "location"]
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")


class EventDeleteView(StaffRequiredMixin, DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("events:event_list")
