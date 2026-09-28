from django.db import models
from django.utils.translation import gettext_lazy as _


class EditableTextBlock(models.Model):
    slug = models.SlugField(
        _("Уникальный идентификатор (Slug)"),
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Используется разработчиком в шаблонах")
    )
    content = models.TextField(_("Содержимое текста"),)

    class Meta:
        verbose_name = _("Редактируемый текстовый блок")
        verbose_name_plural = _("Редактируемые текстовые блоки")
        ordering = ["slug"]

    def __str__(self):
        return self.slug
