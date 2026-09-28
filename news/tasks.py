import logging
import os
import tempfile
from io import BytesIO

from django.conf import settings
from huey.contrib.djhuey import lock_task, task
from PIL import Image

from news.models.posts import ImageProcessingStatus, Post

logger = logging.getLogger(__name__)


@task()
@lock_task('compress-post-image-{0}')
def compress_post_image_task(post_id: int):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return

    if not post.image:
        Post.objects.filter(pk=post_id).update(
            image_processing_status=ImageProcessingStatus.SKIPPED
        )
        return

    Post.objects.filter(pk=post_id).update(
        image_processing_status=ImageProcessingStatus.PROCESSING
    )

    try:
        min_size_bytes = settings.MIN_IMAGE_SIZE_FOR_COMPRESSION_MB * 1024 * 1024
        original_size = post.image.size

        if original_size < min_size_bytes:
            Post.objects.filter(pk=post_id).update(
                image_processing_status=ImageProcessingStatus.SKIPPED
            )
            return

        with post.image.open('rb') as f:
            image = Image.open(f)
            image.load()
            original_format = image.format or 'JPEG'

        max_dim = settings.MAX_IMAGE_DIMENSION_PX
        needs_resize = max(image.size) > max_dim
        needs_recompress = original_format in ('JPEG', 'WEBP')

        if not needs_resize and not needs_recompress:
            Post.objects.filter(pk=post_id).update(
                image_processing_status=ImageProcessingStatus.SKIPPED
            )
            return

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
            Post.objects.filter(pk=post_id).update(
                image_processing_status=ImageProcessingStatus.SKIPPED
            )
            return

        storage_path = post.image.storage.path(post.image.name)
        dir_name = os.path.dirname(storage_path)

        tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name)
        try:
            with os.fdopen(tmp_fd, 'wb') as tmp_file:
                tmp_file.write(buffer.read())
            os.replace(tmp_path, storage_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

        Post.objects.filter(pk=post_id).update(
            image_processing_status=ImageProcessingStatus.DONE
        )
    except Exception:
        logger.exception("Failed to compress image for Post id=%s", post_id)
        Post.objects.filter(pk=post_id).update(
            image_processing_status=ImageProcessingStatus.FAILED
        )
