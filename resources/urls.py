from django.urls import path

from .views import ResourceDetailView, ResourceFilesZipView, ResourceListView

app_name = "resources"

urlpatterns = [
    path("", ResourceListView.as_view(), name="resource_list"),
    path("<slug:slug>/", ResourceDetailView.as_view(), name="resource_detail"),
    path(
        "<slug:slug>/download-all/",
        ResourceFilesZipView.as_view(),
        name="resource_download_all",
    ),
]
