from unittest import mock

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.test import TestCase

from resources.models.resources import ResourceFile
from resources.tasks import delete_file_task
from resources.tests.factories import ResourceFactory
from resources.tests.mixins import MediaCleanupTestMixin


class DeleteFileTaskEdgeCasesTests(MediaCleanupTestMixin, TestCase):

    def test_storage_error_is_logged_and_does_not_raise(self):
        with mock.patch("resources.tasks.default_storage") as storage:
            storage.exists.return_value = True
            storage.delete.side_effect = OSError("disk error")
            with self.assertLogs("resources.tasks", level="ERROR"):
                delete_file_task.call_local("some/path.pdf")

    def test_file_is_not_deleted_if_transaction_rolled_back(self):
        with mock.patch("resources.tasks._compress_image", return_value=False), \
                mock.patch("resources.tasks._compress_pdf", return_value=False), \
                mock.patch("resources.tasks._convert_word_to_pdf", return_value=False):
            obj = ResourceFile.objects.create(
                resource=ResourceFactory(),
                file=ContentFile(b"x", "a.pdf"),
            )
        path = obj.file.name
        pk = obj.pk

        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    obj.delete()
                    raise RuntimeError("rollback")
            except RuntimeError:
                pass

        self.assertTrue(default_storage.exists(path))
        self.assertTrue(ResourceFile.objects.filter(pk=pk).exists())