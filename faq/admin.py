from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import FAQItem


@admin.register(FAQItem)
class FAQItemAdmin(TranslationAdmin):
    list_display = ('question', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'order')
    search_fields = ('question', 'answer')
