import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from common.choices import ImageProcessingStatus
from events.models import Event
from news.models.posts import Post
from resources.tasks import enqueue_file_deletion

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Post)
def track_image_change(sender, instance, **kwargs):
    instance._old_file_paths = None
    if instance.pk:
        try:
            old_image = Post.objects.only('image').get(pk=instance.pk).image
        except Post.DoesNotExist:
            old_image = None
        old_name = old_image.name if old_image else None
        new_name = instance.image.name if instance.image else None
        instance._image_changed = old_name != new_name
        if old_name and old_name != new_name:
            instance._old_file_paths = [old_name]
    else:
        instance._image_changed = bool(instance.image)

@receiver(post_save, sender=Post)
def enqueue_image_compression(sender, instance, **kwargs):
    old_paths = getattr(instance, "_old_file_paths", None)
    if old_paths:
        enqueue_file_deletion(*old_paths)
        instance._old_file_paths = None
        
    if getattr(instance, '_image_changed', False) and instance.image:
        from news.tasks import compress_post_image_task

        Post.objects.filter(pk=instance.pk).update(
            image_processing_status=ImageProcessingStatus.PENDING
        )
        transaction.on_commit(
            lambda pk=instance.pk: compress_post_image_task(pk)
        )
        logger.info("Queued image compression for Post id=%s", instance.pk)

@receiver(post_delete, sender=Post)
def cleanup_post_image(sender, instance, **kwargs):
    enqueue_file_deletion(instance.image.name if instance.image else None)


@receiver(post_delete, sender=Event)
def cleanup_event_image(sender, instance, **kwargs):
    enqueue_file_deletion(instance.image.name if instance.image else None)



@receiver(pre_save, sender=Event)
def track_event_image_change(sender, instance, **kwargs):
    instance._old_file_paths = None
    if not instance.pk:
        return
    old = Event.objects.only('image').filter(pk=instance.pk).first()
    if not old:
        return
    old_name = old.image.name if old.image else None
    new_name = instance.image.name if instance.image else None
    if old_name and old_name != new_name:
        instance._old_file_paths = [old_name]


@receiver(post_save, sender=Event)
def cleanup_replaced_event_image(sender, instance, **kwargs):
    old_paths = getattr(instance, "_old_file_paths", None)
    if old_paths:
        enqueue_file_deletion(*old_paths)
        instance._old_file_paths = None