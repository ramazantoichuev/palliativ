from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from common.choices import ImageProcessingStatus
from news.tests.factories import PostFactory, make_test_image_bytes


class PostSignalsTests(TestCase):
    def test_new_post_with_image_enqueues_task_after_commit(self):
        with mock.patch('news.tasks.compress_post_image_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                post = PostFactory()
            mocked_task.assert_called_once_with(post.pk)

    def test_new_post_sets_status_pending_immediately(self):
        with mock.patch('news.tasks.compress_post_image_task'):
            with self.captureOnCommitCallbacks(execute=False):
                post = PostFactory()
            post.refresh_from_db()
            self.assertEqual(post.image_processing_status, ImageProcessingStatus.PENDING)

    def test_resave_without_image_change_does_not_enqueue_again(self):
        with mock.patch('news.tasks.compress_post_image_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                post = PostFactory()
            mocked_task.reset_mock()

            with self.captureOnCommitCallbacks(execute=True):
                post.title = 'Изменённый заголовок'
                post.save()

            mocked_task.assert_not_called()

    def test_replacing_image_enqueues_task_again(self):
        with mock.patch('news.tasks.compress_post_image_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                post = PostFactory()
            mocked_task.reset_mock()

            with self.captureOnCommitCallbacks(execute=True):
                post.image = SimpleUploadedFile(
                    'new.jpg', make_test_image_bytes(), content_type='image/jpeg'
                )
                post.save()

            mocked_task.assert_called_once_with(post.pk)

    def test_post_without_image_does_not_enqueue(self):
        with mock.patch('news.tasks.compress_post_image_task') as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                PostFactory(image=None)
            mocked_task.assert_not_called()