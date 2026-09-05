from django.urls import path

from .views import DoctorPatientListView, PatientCardDetailView

app_name = 'patients'

urlpatterns = [
    path('my/', DoctorPatientListView.as_view(), name='doctor_dashboard'),
    path('my-card/', PatientCardDetailView.as_view(), name='patient_dashboard'),
]