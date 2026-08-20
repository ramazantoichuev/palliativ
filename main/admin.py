from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models.consultation import ConsultationRequest
# Register your models here.

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'phone', 'email', 'topic', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'topic', 'created_at')
    search_fields = ('first_name', 'phone', 'email')
    ordering = ('-created_at',)
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('first_name', 'phone', 'email', 'topic')
        }),
        (_('Управление заявкой'), {
            'fields': ('status', 'created_at')
        }),
    )
    readonly_fields = ('created_at',)
