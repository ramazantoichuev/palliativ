from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models.resources import Resource, ResourceFile, ResourceVideoLink


class ResourceFileInline(admin.TabularInline):
    model = ResourceFile
    extra = 1

class ResourceVideoLinkInline(admin.TabularInline):
    model = ResourceVideoLink
    extra = 1


@admin.register(Resource)
class ResourceAdmin(TranslationAdmin):
    list_display = ('title', 'audience', 'subcategory', 'created_at')
    list_filter = ('audience', 'subcategory', 'symptoms')
    search_fields = ('title', 'description')
    filter_horizontal = ('symptoms',)
    ordering = ['audience', 'subcategory']
    inlines = [ResourceFileInline, ResourceVideoLinkInline]

    class Media:
        js = ('resources/resources_admin.js',)

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
                    request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')

    def has_permission(self, request, obj=None):
        return request.user.is_authenticated and (
                    request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')

    has_add_permission = has_permission
    has_change_permission = has_permission
    has_delete_permission = has_permission
