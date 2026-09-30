import logging
import os
import subprocess
import tempfile
from io import BytesIO

from django.conf import settings
from huey.contrib.djhuey import lock_task, task
from PIL import Image

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp')
PDF_EXTENSIONS = ('pdf',)
SKIP_EXTENSIONS = ('doc', 'docx')

GHOSTSCRIPT_TIMEOUT_SECONDS = 180


def _get_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def _atomic_replace(storage, name, data: bytes):
    storage_path = storage.path(name)
    dir_name = os.path.dirname(storage_path)

    tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    try:
        with os.fdopen(tmp_fd, 'wb') as tmp_file:
            tmp_file.write(data)
        os.replace(tmp_path, storage_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _compress_image(resource_file, original_size: int) -> bool:
    min_size_bytes = settings.MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB * 1024 * 1024
    if original_size < min_size_bytes:
        return False

    with resource_file.file.open('rb') as f:
        image = Image.open(f)
        image.load()
        original_format = image.format or 'JPEG'

    max_dim = settings.MAX_IMAGE_DIMENSION_PX
    needs_resize = max(image.size) > max_dim
    needs_recompress = original_format in ('JPEG', 'WEBP', 'PNG')

    if not needs_resize and not needs_recompress:
        return False

    if needs_resize:
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    if image.mode in ('RGBA', 'P') and original_format == 'JPEG':
        image = image.convert('RGB')

    buffer = BytesIO()
    save_kwargs = {'format': original_format, 'optimize': True}
    if original_format in ('JPEG', 'WEBP'):
        save_kwargs['quality'] = 80
    image.save(buffer, **save_kwargs)
    buffer.seek(0)

    compressed_size = buffer.getbuffer().nbytes
    if compressed_size >= original_size:
        return False

    _atomic_replace(resource_file.file.storage, resource_file.file.name, buffer.read())
    return True


def _compress_pdf(resource_file, original_size: int) -> bool:
    min_size_bytes = settings.MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB * 1024 * 1024
    if original_size < min_size_bytes:
        return False

    storage_path = resource_file.file.storage.path(resource_file.file.name)
    dir_name = os.path.dirname(storage_path)

    tmp_fd, tmp_output_path = tempfile.mkstemp(dir=dir_name, suffix='.pdf')
    os.close(tmp_fd)

    try:
        result = subprocess.run(
            [
                'gs',
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/ebook',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                f'-sOutputFile={tmp_output_path}',
                storage_path,
            ],
            timeout=GHOSTSCRIPT_TIMEOUT_SECONDS,
            capture_output=True,
        )

        if result.returncode != 0:
            logger.error(
                "Ghostscript failed for ResourceFile id=%s: %s",
                resource_file.pk, result.stderr.decode(errors='replace')
            )
            return False

        compressed_size = os.path.getsize(tmp_output_path)
        if compressed_size == 0 or compressed_size >= original_size:
            return False

        os.replace(tmp_output_path, storage_path)
        return True
    finally:
        if os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)


@task()
@lock_task('compress-resource-file-{0}')
def compress_resource_file_task(resource_file_id: int):
    from common.choices import ImageProcessingStatus
    from resources.models.resources import ResourceFile

    try:
        resource_file = ResourceFile.objects.get(pk=resource_file_id)
    except ResourceFile.DoesNotExist:
        return

    if not resource_file.file:
        ResourceFile.objects.filter(pk=resource_file_id).update(
            processing_status=ImageProcessingStatus.SKIPPED
        )
        return

    ResourceFile.objects.filter(pk=resource_file_id).update(
        processing_status=ImageProcessingStatus.PROCESSING
    )

    try:
        extension = _get_extension(resource_file.file.name)
        original_size = resource_file.file.size

        if extension in SKIP_EXTENSIONS:
            ResourceFile.objects.filter(pk=resource_file_id).update(
                processing_status=ImageProcessingStatus.SKIPPED
            )
            return

        if extension in IMAGE_EXTENSIONS:
            changed = _compress_image(resource_file, original_size)
        elif extension in PDF_EXTENSIONS:
            changed = _compress_pdf(resource_file, original_size)
        else:
            changed = False

        ResourceFile.objects.filter(pk=resource_file_id).update(
            processing_status=ImageProcessingStatus.DONE if changed else ImageProcessingStatus.SKIPPED
        )
    except Exception:
        logger.exception("Failed to compress ResourceFile id=%s", resource_file_id)
        ResourceFile.objects.filter(pk=resource_file_id).update(
            processing_status=ImageProcessingStatus.FAILED
        )