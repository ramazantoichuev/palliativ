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
    limit_px = settings.MAX_IMAGE_DIMENSION_PX
    image = Image.open(file)
    width, height = image.size
    if width > limit_px or height > limit_px:
        raise ValidationError(
            _("Разрешение изображения не должно превышать %(limit)s пикселей по большей стороне."),
            params={"limit": limit_px},
        )


def validate_resource_file_size(file):
    limit_mb = settings.MAX_RESOURCE_FILE_SIZE_MB
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(
            _("Размер файла не должен превышать %(limit)s МБ."),
            params={"limit": limit_mb},
        )