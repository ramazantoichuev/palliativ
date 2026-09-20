from modeltranslation.translator import TranslationOptions, register

from .models.resources import Resource
from .models.terms import Term


@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ("title", "description")

@register(Term)
class TermTranslationOptions(TranslationOptions):
    fields = ('name', 'definition')