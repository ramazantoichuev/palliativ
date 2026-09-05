from django.views.generic import DetailView, ListView

from .models.resources import Resource


class ResourceListView(ListView):
    model = Resource
    template_name = 'resources/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 12

    def get_queryset(self):
        queryset = Resource.objects.all().order_by('-created_at')

        audience = self.request.GET.get('audience')
        subcategory = self.request.GET.get('subcategory')
        symptom = self.request.GET.get('symptom')

        if audience:
            queryset = queryset.filter(audience=audience)
        if subcategory:
            queryset = queryset.filter(subcategory=subcategory)
        if symptom:
            queryset = queryset.filter(symptoms__id=symptom)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        from patients.models.patients import Symptom
        context = super().get_context_data(**kwargs)
        context['audience_choices'] = Resource.AUDIENCE_CHOICES
        context['subcategory_choices'] = Resource.SUBCATEGORY_CHOICES
        context['symptoms'] = Symptom.objects.all()
        context['selected_audience'] = self.request.GET.get('audience', '')
        context['selected_subcategory'] = self.request.GET.get('subcategory', '')
        context['selected_symptom'] = self.request.GET.get('symptom', '')
        return context


class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'resources/resource_detail.html'
    context_object_name = 'resource'

# Create your views here.
