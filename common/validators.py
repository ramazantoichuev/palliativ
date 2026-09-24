from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError


def validate_image_size(file):
    limit_mb = settings.MAX_IMAGE_SIZE_MB
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(
            _("Размер изображения не должен превышать %(limit)s МБ."),
            params={"limit": limit_mb},
        )


def validate_image_integrity(file):

    file.seek(0)
    try:
        image = Image.open(file)
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError(
            _("Файл повреждён или не является корректным изображением.")
        )
    finally:
        file.seek(0)


def validate_resource_file_size(file):
    limit_mb = settings.MAX_RESOURCE_FILE_SIZE_MB
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(
            _("Размер файла не должен превышать %(limit)s МБ."),
            params={"limit": limit_mb},
        )

def validate_image_dimensions(file):
    """
    Оставлена для обратной совместимости со старыми миграциями
    (использовалась в validators= ImageField в предыдущих версиях).
    Больше не применяется как активный валидатор.
    """
