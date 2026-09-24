import logging

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from common.choices import ImageProcessingStatus
from resources.models.resources import ResourceFile

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ResourceFile)
def track_file_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_file = ResourceFile.objects.only('file').get(pk=instance.pk).file
        except ResourceFile.DoesNotExist:
            old_file = None
        instance._file_changed = (old_file.name if old_file else None) != (
            instance.file.name if instance.file else None
        )
    else:
        instance._file_changed = bool(instance.file)


@receiver(post_save, sender=ResourceFile)
def enqueue_file_compression(sender, instance, **kwargs):
    if getattr(instance, '_file_changed', False) and instance.file:
        from resources.tasks import compress_resource_file_task

        ResourceFile.objects.filter(pk=instance.pk).update(
            processing_status=ImageProcessingStatus.PENDING
        )
        transaction.on_commit(
            lambda pk=instance.pk: compress_resource_file_task(pk)
        )
        logger.info("Queued file compression for ResourceFile id=%s", instance.pk)