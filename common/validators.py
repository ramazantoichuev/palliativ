from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image


def validate_image_size(file):
    limit_mb = settings.MAX_IMAGE_SIZE_MB
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(
            _("Размер изображения не должен превышать %(limit)s МБ."),
            params={"limit": limit_mb},
        )


def validate_image_dimensions(file):
    """
    Оставлена для обратной совместимости со старыми миграциями
    (использовалась в validators= ImageField).
    Больше не применяется как активный валидатор — ограничение
    разрешения теперь обрабатывается в фоновой задаче сжатия (Ticket 66).
    """
    pass





















def validate_resource_file_size(file):
    limit_mb = settings.MAX_RESOURCE_FILE_SIZE_MB
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(
            _("Размер файла не должен превышать %(limit)s МБ."),
            params={"limit": limit_mb},
        )