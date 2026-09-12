from django.urls import path

from .views import ResourceDetailView, ResourceListView

app_name = "resources"

urlpatterns = [
    path("", ResourceListView.as_view(), name="resource_list"),
    path("<slug:slug>/", ResourceDetailView.as_view(), name="resource_detail"),
]
