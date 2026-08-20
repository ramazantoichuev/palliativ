from django.urls import path
from .views import (
    EventListView, EventDetailView,
    EventCreateView, EventUpdateView, EventDeleteView
)

app_name = 'events'

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('<slug:slug>/edit/', EventUpdateView.as_view(), name='event_edit'),
    path('<slug:slug>/delete/', EventDeleteView.as_view(), name='event_delete'),
]