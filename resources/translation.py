from modeltranslation.translator import TranslationOptions, register
from models.terms import Term

from .models.resources import Resource


@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ("title", "description")

@register(Term)
class TermTranslationOptions(TranslationOptions):
    fields = ('name', 'definition')