from modeltranslation.translator import TranslationOptions, register

from .models.patients import Symptom


@register(Symptom)
class SymptomTranslationOptions(TranslationOptions):
    fields = ('name',)