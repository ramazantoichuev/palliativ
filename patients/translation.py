from modeltranslation.translator import register, TranslationOptions
from .models.patients import Symptom


@register(Symptom)
class SymptomTranslationOptions(TranslationOptions):
    fields = ('name',)