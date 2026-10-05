import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from common.choices import ImageProcessingStatus
from resources.models.resources import ResourceFile
from resources.tasks import enqueue_file_deletion

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ResourceFile)
def track_file_change(sender, instance, **kwargs):
    instance._old_file_paths = None
    if instance.pk:
        try:
            old = ResourceFile.objects.get(pk=instance.pk)
        except ResourceFile.DoesNotExist:
            old = None
        old_name = old.file.name if old and old.file else None
        new_name = instance.file.name if instance.file else None
        instance._file_changed = old_name != new_name
        if old_name and old_name != new_name:
            instance._old_file_paths = [
                old_name,
                getattr(getattr(old, "converted_pdf", None), "name", None),
            ]
    else:
        instance._file_changed = bool(instance.file)


@receiver(post_save, sender=ResourceFile)
def enqueue_file_compression(sender, instance, **kwargs):
    old_paths = getattr(instance, "_old_file_paths", None)
    if old_paths:
        enqueue_file_deletion(*old_paths)
        instance._old_file_paths = None

    if getattr(instance, '_file_changed', False) and instance.file:
        from resources.tasks import compress_resource_file_task

        ResourceFile.objects.filter(pk=instance.pk).update(
            processing_status=ImageProcessingStatus.PENDING
        )
        transaction.on_commit(
            lambda pk=instance.pk: compress_resource_file_task(pk)
        )
        logger.info("Queued file compression for ResourceFile id=%s", instance.pk)

@receiver(post_delete, sender=ResourceFile)
def cleanup_resource_file(sender, instance, **kwargs):
    paths = [instance.file.name if instance.file else None]
    if instance.converted_pdf:
        paths.append(instance.converted_pdf.name)
    enqueue_file_deletion(*paths)