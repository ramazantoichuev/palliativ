from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.urls import reverse, reverse_lazy
from accounts.models import BaseUser
from .models import Event
from .forms import EventRegistrationForm
from django.utils.text import slugify


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ только для admin и moderator"""
    def test_func(self):
        return self.request.user.role in [BaseUser.Role.ADMIN, BaseUser.Role.MODERATOR]


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['upcoming_events'] = Event.objects.filter(event_date__gte=now).order_by('event_date')
        context['past_events'] = Event.objects.filter(event_date__lt=now).order_by('-event_date')
        return context


class EventDetailView(FormMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    form_class = EventRegistrationForm

    def get_success_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.object.slug})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = self.object
            registration.save()
            return self.form_valid(form)
        return self.form_invalid(form)

class EventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    fields = ['title', 'description', 'image', 'event_date', 'location']
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)

class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    fields = ['title', 'description', 'image', 'event_date', 'location']
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')


class EventDeleteView(StaffRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')
# Create your views here.
