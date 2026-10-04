from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from simple_history.admin import SimpleHistoryAdmin

from accounts.models import BaseUser

from .models.consultation import ConsultationRequest
from .models.editable_text_block import EditableTextBlock
from .models.site_contacts import SiteContacts
from .models.system_settings import SystemSettings
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


class PageFilter(admin.SimpleListFilter):
    title = _("Страница")
    parameter_name = "page"

    PAGES = {
        "home": _("Главная"),
        "about": _("О нас"),
    }

    def lookups(self, request, model_admin):
        return list(self.PAGES.items())

    def queryset(self, request, queryset):
        if self.value() in self.PAGES:
            return queryset.filter(slug__startswith=f"{self.value()}_")
        return queryset


@admin.register(EditableTextBlock)
class EditableTextBlockAdmin(SimpleHistoryAdmin, TranslationAdmin):
    search_fields = ("slug", "content")
    list_display = ("slug", "is_deleted", "deleted_at")
    list_filter = ("is_deleted", PageFilter)
    ordering = ("slug",)
    actions = ["restore_selected"]

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", "")
            in (BaseUser.Role.ADMIN, BaseUser.Role.MANAGER)
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            readonly.append("slug")
        return readonly

    def delete_model(self, request, obj):
        obj.soft_delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.soft_delete()

    @admin.action(description=_("Восстановить выбранные"))
    def restore_selected(self, request, queryset):
        restored_count = 0
        conflict_slugs = []

        for obj in queryset:
            if not obj.is_deleted:
                continue
            conflict_exists = (
                EditableTextBlock.all_objects
                .filter(slug=obj.slug, is_deleted=False)
                .exclude(pk=obj.pk)
                .exists()
            )
            if conflict_exists:
                conflict_slugs.append(obj.slug)
                continue
            obj.restore()
            restored_count += 1

        if restored_count:
            self.message_user(
                request,
                _("Восстановлено записей: %(count)s.") % {"count": restored_count},
                level=messages.SUCCESS,
            )
        if conflict_slugs:
            self.message_user(
                request,
                _(
                    "Не удалось восстановить: slug уже занят другой активной "
                    "записью — %(slugs)s."
                ) % {"slugs": ", ".join(conflict_slugs)},
                level=messages.ERROR,
            )

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ("patient_registration_enabled", "doctor_registration_enabled")

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", "")
            in (BaseUser.Role.ADMIN, BaseUser.Role.MANAGER)
        )

    def has_add_permission(self, request):
        return self.has_module_permission(request) and not SystemSettings.objects.exists()

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


@admin.register(SiteContacts)
class SiteContactsAdmin(TranslationAdmin):
    list_display = ("phone_display", "email", "address")

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or getattr(request.user, "role", "")
            in (BaseUser.Role.ADMIN, BaseUser.Role.MANAGER)
        )

    def has_add_permission(self, request):
        return self.has_module_permission(request) and not SiteContacts.objects.exists()

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
