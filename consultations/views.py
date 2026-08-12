from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import ConsultationRequest
from .forms import ConsultationForm

class ConsultationCreateView(CreateView):
    model = ConsultationRequest
    form_class = ConsultationForm
    template_name = 'consultations/consultation.html'
    success_url = reverse_lazy('consultations:success')


# Create your views here.
