from django.contrib import admin, messages
from django.db.models import Case, IntegerField, Value, When
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from simple_history.admin import SimpleHistoryAdmin

from accounts.models import BaseUser

from .models.consultation import ConsultationRequest
from .models.editable_text_block import EditableTextBlock
from .models.site_contacts import SiteContacts
from .models.system_settings import SystemSettings
from .models.team import TeamMember

STATUS_PRIORITY = Case(
    When(status="new", then=Value(0)),
    When(status="in_progress", then=Value(1)),
    default=Value(2),
    output_field=IntegerField(),
)

ACTIVE_STATUSES = ("new", "in_progress")


class StatusGroupFilter(admin.SimpleListFilter):
    title = _("Статус заявки")
    parameter_name = "status_group"

    def lookups(self, request, model_admin):
        return [
            ("active", _("Активные")),
            *ConsultationRequest.STATUS_CHOICES,
        ]

    def value(self):
        return super().value() or "active"

    def choices(self, changelist):
        current = self.value()
        for lookup, title in self.lookup_choices:
            if lookup == "active":
                # «Активные» — состояние по умолчанию: параметр убираем из URL
                query = changelist.get_query_string(remove=[self.parameter_name])
            else:
                query = changelist.get_query_string({self.parameter_name: lookup})
            yield {
                "selected": current == lookup,
                "query_string": query,
                "display": title,
            }
        yield {
            "selected": current == "all",
            "query_string": changelist.get_query_string({self.parameter_name: "all"}),
            "display": _("Все"),
        }

    def queryset(self, request, queryset):
        value = self.value()
        if value == "active":
            return queryset.filter(status__in=ACTIVE_STATUSES)
        if value == "all":
            return queryset
        return queryset.filter(status=value)


# Register your models here.
@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "phone", "email", "topic", "status", "created_at")
    list_editable = ("status",)
    list_filter = (StatusGroupFilter, "topic", "created_at")
    search_fields = ("first_name", "phone", "email")
    actions = ["mark_in_progress", "mark_closed", "mark_rejected"]
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("first_name", "phone", "email", "topic")},
        ),
        (_("Управление заявкой"), {"fields": ("status", "created_at")}),
    )
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        # super().get_queryset() сам вызывает order_by(get_ordering()) до появления
        # аннотации, поэтому собираем queryset вручную: сначала annotate, потом order_by
        qs = self.model._default_manager.get_queryset().annotate(
            _status_priority=STATUS_PRIORITY
        )
        return qs.order_by(*self.get_ordering(request))

    def get_ordering(self, request):
        return ["_status_priority", "-created_at", "-pk"]

    def _bulk_set_status(self, request, queryset, status):
        updated = queryset.update(status=status)
        self.message_user(
            request,
            _("Обновлено заявок: %(count)s") % {"count": updated},
            level=messages.SUCCESS,
        )

    @admin.action(description=_("Взять в работу"))
    def mark_in_progress(self, request, queryset):
        self._bulk_set_status(request, queryset, "in_progress")

    @admin.action(description=_("Отметить рассмотренными"))
    def mark_closed(self, request, queryset):
        self._bulk_set_status(request, queryset, "closed")

    @admin.action(description=_("Отклонить"))
    def mark_rejected(self, request, queryset):
        self._bulk_set_status(request, queryset, "rejected")


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