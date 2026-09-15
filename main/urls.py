from django.urls import path

from .views import (
    AboutView,
    ConsultationCreateView,
    ContactsView,
    HomeView,
    PrivacyPolicyView,
)

app_name = "main"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("consultation/", ConsultationCreateView.as_view(), name="new-consultation"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
]
