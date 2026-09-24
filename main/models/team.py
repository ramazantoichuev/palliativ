from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.validators import validate_image_size


class TeamMember(models.Model):
    class Category(models.TextChoices):
        FOUNDER = "founder", _("Учредители")
        AMBASSADOR = "ambassador", _("Посол Доброй воли")
        BOARD = "board", _("Управляющий совет")
        TEAM = "team", _("Команда Ассоциации")

    full_name = models.CharField(_("ФИО / название организации"), max_length=255)
    position = models.CharField(_("Должность"), max_length=255, blank=True)
    bio = models.TextField(_("Краткая информация"), blank=True)
    category = models.CharField(
        _("Категория"), max_length=20, choices=Category.choices
    )
    photo = models.ImageField(
        _("Фотография"),
        upload_to="team/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            validate_image_size,
        ],
    )
    order = models.PositiveIntegerField(_("Порядок отображения"), default=0)

    class Meta:
        verbose_name = _("Член команды")
        verbose_name_plural = _("Команда и руководство")
        ordering = ["order", "id"]

    def __str__(self):
        return self.full_name
