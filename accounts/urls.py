from django.urls import path
from .views import CustomLoginView, WaitingApprovalView

app_name = 'accounts'


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('waiting-approval/', WaitingApprovalView.as_view(), name='waiting_approval'),
]