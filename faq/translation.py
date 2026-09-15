from modeltranslation.translator import TranslationOptions, register

from .models import FAQItem


@register(FAQItem)
class FAQItemTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')
