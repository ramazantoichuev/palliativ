from django.urls import path
from .views import ConsultationCreateView

app_name = 'consultations'

urlpatterns = [
    path('consultation/', ConsultationCreateView.as_view(), name='consultation'),
]