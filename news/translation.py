from modeltranslation.translator import TranslationOptions, translator

from .models import Category, Post


class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'description')
    required_languages = ('ru',)


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('ru',)


translator.register(Post, PostTranslationOptions)
translator.register(Category, CategoryTranslationOptions)