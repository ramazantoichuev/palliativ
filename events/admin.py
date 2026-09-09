from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from accounts.models import BaseUser
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(TranslationAdmin):
    list_filter = ('event_date', 'title', 'location')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}

    def get_list_display(self, request):
        base_fields = ('title', 'description', 'event_date', 'location')
        if request.user.role in [BaseUser.Role.ADMIN, BaseUser.Role.MANAGER]:
            return base_fields + ('registrations_count',)
        return base_fields

    def registrations_count(self, obj):
        return obj.registrations.count()
    registrations_count.short_description = _('Зарегистрировано')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'event', 'email', 'phone', 'created_at', 'status')