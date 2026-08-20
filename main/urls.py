from django.urls import path
from .views import HomeView, AboutView
from .views import ConsultationCreateView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('consultation/', ConsultationCreateView.as_view(), name='new-consultation'),
]
