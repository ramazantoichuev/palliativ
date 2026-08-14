from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from .models import Event
from .forms import EventRegistrationForm


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
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
# Create your views here.
