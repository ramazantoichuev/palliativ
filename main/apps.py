from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"
    verbose_name = _("Главная")

    def ready(self):
        from simple_history import register

        from .models.editable_text_block import EditableTextBlock

        register(EditableTextBlock, app=self.label)