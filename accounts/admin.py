from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import BaseUser, DoctorProfile, PatientProfile


# Register your models here.
class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = _("Медицинский профиль врача")


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = _("Медицинская карта пациента")


@admin.register(BaseUser)
class BaseUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "role",
        "is_approved",
        "is_staff",
    )
    list_filter = ("role", "is_approved", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        (_("Системная роль"), {"fields": ("role", "is_approved")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            _("Выбор роли для нового пользователя"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "is_approved",
                    "phone",
                ),
            },
        ),
    )

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == BaseUser.Role.DOCTOR:
                return [DoctorProfileInline]
            elif obj.role == BaseUser.Role.PATIENT:
                return [PatientProfileInline]
        return []


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_child")
    list_filter = ("is_child",)
    search_fields = ["user__first_name", "user__last_name", "user__email"]


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__last_name", "user__email"]
