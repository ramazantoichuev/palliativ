from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models.posts import Category, Post


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    readonly_fields = ['image_processing_status']
    list_display = ('title', 'category', 'created_at','image_processing_status')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}