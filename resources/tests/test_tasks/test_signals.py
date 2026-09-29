from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from common.choices import ImageProcessingStatus
from resources.tests.factories import (
    ResourceFactory,
    ResourceFileFactory,
    make_test_image_bytes,
)


class ResourceFileSignalsTests(TestCase):
    def test_new_file_enqueues_task_after_commit(self):
        resource = ResourceFactory()
        with mock.patch('resources.tasks.compress_resource_file_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                rf = ResourceFileFactory(resource=resource)
            mocked_task.assert_called_once_with(rf.pk)

    def test_new_file_sets_status_pending_immediately(self):
        resource = ResourceFactory()
        with mock.patch('resources.tasks.compress_resource_file_task'):
            with self.captureOnCommitCallbacks(execute=False):
                rf = ResourceFileFactory(resource=resource)
            rf.refresh_from_db()
            self.assertEqual(rf.processing_status, ImageProcessingStatus.PENDING)

    def test_resave_without_file_change_does_not_enqueue_again(self):
        resource = ResourceFactory()
        with mock.patch('resources.tasks.compress_resource_file_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                rf = ResourceFileFactory(resource=resource)
            mocked_task.reset_mock()

            with self.captureOnCommitCallbacks(execute=True):
                rf.resource = resource
                rf.save()

            mocked_task.assert_not_called()

    def test_replacing_file_enqueues_task_again(self):
        resource = ResourceFactory()
        with mock.patch('resources.tasks.compress_resource_file_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                rf = ResourceFileFactory(resource=resource)
            mocked_task.reset_mock()

            with self.captureOnCommitCallbacks(execute=True):
                rf.file = SimpleUploadedFile(
                    'new.jpg', make_test_image_bytes(), content_type='image/jpeg'
                )
                rf.save()

            mocked_task.assert_called_once_with(rf.pk)