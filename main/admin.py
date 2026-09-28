from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from accounts.models import BaseUser

from .models.consultation import ConsultationRequest
from .models.editable_text_block import EditableTextBlock
from .models.team import TeamMember


# Register your models here.
@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "phone", "email", "topic", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "topic", "created_at")
    search_fields = ("first_name", "phone", "email")
    ordering = ("-created_at",)
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("first_name", "phone", "email", "topic")},
        ),
        (_("Управление заявкой"), {"fields": ("status", "created_at")}),
    )
    readonly_fields = ("created_at",)

@admin.register(EditableTextBlock)
class EditableTextBlockAdmin(TranslationAdmin):
    list_display = ("slug",)
    search_fields = ("slug", "content")
    ordering = ("slug",)

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", "")
            in (BaseUser.Role.ADMIN, BaseUser.Role.MANAGER)
        )

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(TeamMember)
class TeamMemberAdmin(TranslationAdmin):
    list_display = ("full_name", "category", "position", "order")
    list_editable = ("order",)
    list_filter = ("category",)
    search_fields = ("full_name", "position", "bio")
    ordering = ("category", "order")

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", "")
            in (BaseUser.Role.ADMIN, BaseUser.Role.MANAGER)
        )

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
