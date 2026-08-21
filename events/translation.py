from modeltranslation.translator import TranslationOptions, translator

from .models import Event


class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'content')
    required_languages = ('ru',)


translator.register(Event, EventTranslationOptions)
