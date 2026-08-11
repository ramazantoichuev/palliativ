from django.urls import path
from .views import CustomLoginView, WaitingApprovalView, RegisterView

app_name = 'accounts'


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('waiting-approval/', WaitingApprovalView.as_view(), name='waiting_approval'),
]