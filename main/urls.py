from django.urls import path

from .views import AboutView, ConsultationCreateView, ContactsView, HomeView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('consultation/', ConsultationCreateView.as_view(), name='new-consultation'),
]
