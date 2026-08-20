from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BaseUser, DoctorProfile, PatientProfile


# Register your models here.
class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Медицинский профиль врача'


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Медицинская карта пациента'


@admin.register(BaseUser)
class BaseUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name','phone', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Системная роль', {'fields': ('role', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Выбор роли для нового пользователя', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'is_approved','phone'),
        }),
    )
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == BaseUser.Role.DOCTOR:
                return [DoctorProfileInline]
            elif obj.role == BaseUser.Role.PATIENT:
                return [PatientProfileInline]
        return []
