from django.urls import path
from .views import FAQListView

app_name = 'faq'

urlpatterns = [
    path('', FAQListView.as_view(), name='faq_list'),
]
