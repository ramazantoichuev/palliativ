from modeltranslation.translator import TranslationOptions, translator

from .models.editable_text_block import EditableTextBlock


class EditableTextBlockTranslationOptions(TranslationOptions):
    fields = ("content",)
    required_languages = ("ru",)

translator.register(EditableTextBlock, EditableTextBlockTranslationOptions)
