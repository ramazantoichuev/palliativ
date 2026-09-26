from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from common.choices import ImageProcessingStatus
from news.tasks import compress_post_image_task
from news.tests.factories import PostFactory, make_test_image_bytes

TEST_OVERRIDES = dict(
    MIN_IMAGE_SIZE_FOR_COMPRESSION_MB=0.001,  # ~1 КБ — тестовые картинки маленькие
    MAX_IMAGE_DIMENSION_PX=10,  # заставляет реальные тестовые картинки ресайзиться
)


class CompressPostImageTaskMissingObjectTests(TestCase):
    def test_missing_post_returns_silently(self):
        compress_post_image_task.call_local(999999)


@override_settings(**TEST_OVERRIDES)
class CompressPostImageTaskNoImageTests(TestCase):
    def test_no_image_marks_skipped(self):
        post = PostFactory(image=None)
        compress_post_image_task.call_local(post.pk)
        post.refresh_from_db()
        self.assertEqual(post.image_processing_status, ImageProcessingStatus.SKIPPED)


class CompressPostImageTaskThresholdTests(TestCase):
    def test_image_below_min_size_is_skipped(self):
        with override_settings(MIN_IMAGE_SIZE_FOR_COMPRESSION_MB=100):
            post = PostFactory()
            compress_post_image_task.call_local(post.pk)
        post.refresh_from_db()
        self.assertEqual(post.image_processing_status, ImageProcessingStatus.SKIPPED)


@override_settings(**TEST_OVERRIDES)
class CompressPostImageTaskSuccessTests(TestCase):
    def test_successful_compression_marks_done_and_shrinks_file(self):
        post = PostFactory(
            image=SimpleUploadedFile(
                'big.jpg',
                make_test_image_bytes(size=(200, 200), quality=100),
                content_type='image/jpeg',
            )
        )
        original_size = post.image.size

        compress_post_image_task.call_local(post.pk)

        post.refresh_from_db()
        self.assertEqual(post.image_processing_status, ImageProcessingStatus.DONE)
        self.assertLess(post.image.size, original_size)

    def test_resize_applied_when_dimension_exceeds_limit(self):
        post = PostFactory(
            image=SimpleUploadedFile(
                'big.jpg',
                make_test_image_bytes(size=(200, 200), quality=100),
                content_type='image/jpeg',
            )
        )

        compress_post_image_task.call_local(post.pk)

        post.refresh_from_db()
        from PIL import Image
        with post.image.open('rb') as f:
            img = Image.open(f)
            self.assertLessEqual(max(img.size), 10)


@override_settings(**TEST_OVERRIDES)
class CompressPostImageTaskErrorTests(TestCase):
    def test_corrupted_image_marks_failed_and_preserves_original(self):
        full_bytes = make_test_image_bytes(size=(300, 300), quality=100)
        broken_bytes = full_bytes[:int(len(full_bytes) * 0.7)]
        post = PostFactory(
            image=SimpleUploadedFile('broken.jpg', broken_bytes, content_type='image/jpeg')
        )
        original_size = post.image.size

        compress_post_image_task.call_local(post.pk)

        post.refresh_from_db()
        self.assertEqual(post.image_processing_status, ImageProcessingStatus.FAILED)
        self.assertEqual(post.image.size, original_size)


@override_settings(**TEST_OVERRIDES)
class CompressPostImageTaskNoGainTests(TestCase):
    def test_no_gain_from_compression_is_skipped_and_file_untouched(self):
        post = PostFactory(
            image=SimpleUploadedFile(
                'small.jpg',
                make_test_image_bytes(size=(20, 20), color='red', quality=95),
                content_type='image/jpeg',
            )
        )
        original_size = post.image.size

        with mock.patch('news.tasks.Image.open') as mocked_open:
            fake_image = mock.Mock()
            fake_image.format = 'JPEG'
            fake_image.size = (20, 20)
            fake_image.mode = 'RGB'
            fake_image.load.return_value = None

            def fake_save(buffer, **kwargs):
                buffer.write(b'0' * (original_size + 1000))  # заведомо больше оригинала

            fake_image.save.side_effect = fake_save
            fake_image.thumbnail.return_value = None
            mocked_open.return_value = fake_image

            compress_post_image_task.call_local(post.pk)

        post.refresh_from_db()
        self.assertEqual(post.image_processing_status, ImageProcessingStatus.SKIPPED)
        self.assertEqual(post.image.size, original_size)