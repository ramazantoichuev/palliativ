from django.urls import path
from .views import ConsultationCreateView

app_name = 'main'

urlpatterns = [
    path('consultation/', ConsultationCreateView.as_view(), name='new-consultation'),
]