from django.db import models
from django.utils.translation import gettext_lazy as _


class ImageProcessingStatus(models.TextChoices):
    PENDING = 'pending', _('В очереди')
    PROCESSING = 'processing', _('Обрабатывается')
    DONE = 'done', _('Обработано')
    FAILED = 'failed', _('Ошибка обработки')
    SKIPPED = 'skipped', _('Сжатие не требуется')