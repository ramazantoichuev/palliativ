from modeltranslation.translator import TranslationOptions, translator

from .models.editable_text_block import EditableTextBlock
from .models.team import TeamMember


class EditableTextBlockTranslationOptions(TranslationOptions):
    fields = ("content",)
    required_languages = ("ru",)


class TeamMemberTranslationOptions(TranslationOptions):
    fields = ("full_name", "position", "bio")
    required_languages = ("ru",)


translator.register(EditableTextBlock, EditableTextBlockTranslationOptions)
translator.register(TeamMember, TeamMemberTranslationOptions)
