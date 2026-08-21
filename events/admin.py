from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(TranslationAdmin):
    list_display = ('title', 'description', 'event_date', 'location')
    list_filter = ('event_date','title', 'location')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'event', 'email', 'phone', 'created_at', 'status')

# Register your models here.
