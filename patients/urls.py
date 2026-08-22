from django.urls import path
from .views import DoctorPatientListView

app_name = 'patients'

urlpatterns = [
    path('my/', DoctorPatientListView.as_view(), name='doctor_dashboard'),
]