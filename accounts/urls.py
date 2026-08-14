from django.urls import path
from .views import CustomLoginView, WaitingApprovalView, PatientRegisterView, DoctorRegisterView  # , about

app_name = 'accounts'


urlpatterns = [
    path('register/patient/', PatientRegisterView.as_view(), name='patient_register'),
    path('register/doctor/', DoctorRegisterView.as_view(), name='doctor_register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('waiting-approval/', WaitingApprovalView.as_view(), name='waiting_approval'),
]
