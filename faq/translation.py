from modeltranslation.translator import register, TranslationOptions
from .models import FAQItem


@register(FAQItem)
class FAQItemTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')
