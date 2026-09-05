from modeltranslation.translator import TranslationOptions, register

from .models.resources import Resource


@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')