# main/models/editable_text_block.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EditableTextBlockQuerySet(models.QuerySet):
    def soft_delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def restore(self):
        return self.update(is_deleted=False, deleted_at=None)


class EditableTextBlockManager(models.Manager):
    def get_queryset(self):
        return EditableTextBlockQuerySet(self.model, using=self._db).filter(is_deleted=False)


class EditableTextBlockAllManager(models.Manager):
    def get_queryset(self):
        return EditableTextBlockQuerySet(self.model, using=self._db)


class EditableTextBlock(models.Model):
    slug = models.SlugField(
        _("Уникальный идентификатор (Slug)"),
        max_length=100,
        db_index=True,
        help_text=_("Используется разработчиком в шаблонах")
    )
    content = models.TextField(_("Содержимое текста"))

    is_deleted = models.BooleanField(_("Удалён"), default=False)
    deleted_at = models.DateTimeField(_("Дата удаления"), null=True, blank=True)

    objects = EditableTextBlockManager()
    all_objects = EditableTextBlockAllManager()

    class Meta:
        verbose_name = _("Редактируемый текстовый блок")
        verbose_name_plural = _("Редактируемые текстовые блоки")
        ordering = ["slug"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(is_deleted=False),
                name="unique_slug_for_active_blocks",
            ),
        ]

    def __str__(self):
        return self.slug

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])