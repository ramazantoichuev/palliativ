import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from news.models.posts import ImageProcessingStatus, Post

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Post)
def track_image_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_image = Post.objects.only('image').get(pk=instance.pk).image
        except Post.DoesNotExist:
            old_image = None
        instance._image_changed = (old_image.name if old_image else None) != (
            instance.image.name if instance.image else None
        )
    else:
        instance._image_changed = bool(instance.image)


@receiver(post_save, sender=Post)
def enqueue_image_compression(sender, instance, **kwargs):
    if getattr(instance, '_image_changed', False) and instance.image:
        from news.tasks import compress_post_image_task

        Post.objects.filter(pk=instance.pk).update(
            image_processing_status=ImageProcessingStatus.PENDING
        )
        compress_post_image_task(instance.pk)
        logger.info("Queued image compression for Post id=%s", instance.pk)