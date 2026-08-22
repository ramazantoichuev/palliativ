from modeltranslation.translator import register, TranslationOptions
from .models.resources import Resource

@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')