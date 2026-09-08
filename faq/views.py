from django.views.generic import ListView
from .models import FAQItem

class FAQListView(ListView):
    model = FAQItem
    template_name = 'faq/faq_list.html'
    context_object_name = 'faq_items'

    def get_queryset(self):
        return FAQItem.objects.filter(is_active=True)
