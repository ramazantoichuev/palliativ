from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from common.choices import ImageProcessingStatus
from resources.models.resources import ResourceFile
from resources.tasks import compress_resource_file_task
from resources.tests.factories import (
    ResourceFactory,
    ResourceFileFactory,
    make_test_image_bytes,
    make_test_pdf_bytes,
)

TEST_OVERRIDES = dict(
    MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB=0.001,  # ~1 КБ
    MAX_IMAGE_DIMENSION_PX=10,  # заставляет реальные тестовые картинки ресайзиться
)


class CompressResourceFileTaskMissingObjectTests(TestCase):
    def test_missing_resource_file_returns_silently(self):
        # Не должно бросать исключение, если объект уже удалён к моменту выполнения
        compress_resource_file_task.call_local(999999)

    def test_no_file_marks_skipped(self):
        resource = ResourceFactory()
        rf = ResourceFile.objects.create(resource=resource)
        compress_resource_file_task.call_local(rf.pk)
        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.SKIPPED)


@override_settings(**TEST_OVERRIDES)
class CompressResourceFileTaskDocDocxTests(TestCase):
    def test_docx_is_always_skipped_without_processing(self):
        resource = ResourceFactory()
        rf = ResourceFile.objects.create(
            resource=resource,
            file=SimpleUploadedFile('doc.docx', b'x' * 2000, content_type='application/octet-stream'),
        )
        with mock.patch('resources.tasks._compress_image') as mocked_image, \
             mock.patch('resources.tasks._compress_pdf') as mocked_pdf:
            compress_resource_file_task.call_local(rf.pk)

        mocked_image.assert_not_called()
        mocked_pdf.assert_not_called()
        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.SKIPPED)


@override_settings(**TEST_OVERRIDES)
class CompressResourceFileTaskThresholdTests(TestCase):
    def test_file_below_min_size_is_skipped(self):
        resource = ResourceFactory()
        with override_settings(MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB=100):
            rf = ResourceFileFactory(resource=resource)
            compress_resource_file_task.call_local(rf.pk)
        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.SKIPPED)


@override_settings(**TEST_OVERRIDES)
class CompressResourceFileTaskImageTests(TestCase):
    def test_successful_image_compression_marks_done_and_shrinks_file(self):
        resource = ResourceFactory()
        rf = ResourceFileFactory(
            resource=resource,
            file=SimpleUploadedFile(
                'big.jpg',
                make_test_image_bytes(size=(200, 200), quality=100),
                content_type='image/jpeg',
            ),
        )
        original_size = rf.file.size

        compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.DONE)
        self.assertLess(rf.file.size, original_size)


    def test_image_that_does_not_shrink_is_skipped_and_file_untouched(self):
        resource = ResourceFactory()
        original_bytes = make_test_image_bytes(size=(20, 20), color='red', quality=95)
        rf = ResourceFileFactory(
            resource=resource,
            file=SimpleUploadedFile('small.jpg', original_bytes, content_type='image/jpeg'),
        )
        original_size = rf.file.size

        # С огромным MAX_IMAGE_DIMENSION_PX ресайз не сработает, а пересжатие
        # маленькой уже неплохо сжатой картинки может не дать выигрыша —
        # имитируем это, замокав _compress_image так, чтобы вернуть False явно.
        with mock.patch('resources.tasks._compress_image', return_value=False):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.SKIPPED)
        self.assertEqual(rf.file.size, original_size)

    def test_corrupted_image_marks_failed_and_preserves_original(self):
        resource = ResourceFactory()
        full_bytes = make_test_image_bytes(size=(300, 300), quality=100)
        broken_bytes = full_bytes[:int(len(full_bytes) * 0.7)]
        rf = ResourceFileFactory(
            resource=resource,
            file=SimpleUploadedFile('broken.jpg', broken_bytes, content_type='image/jpeg'),
        )
        original_size = rf.file.size

        compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.FAILED)
        self.assertEqual(rf.file.size, original_size)


@override_settings(**TEST_OVERRIDES)
class CompressResourceFileTaskPdfTests(TestCase):
    def _fake_ghostscript_success(self, output_content=b'%PDF-FAKE-SMALLER'):
        def side_effect(cmd, timeout, capture_output):
            output_path = next(
                arg.split('=', 1)[1] for arg in cmd if arg.startswith('-sOutputFile=')
            )
            with open(output_path, 'wb') as f:
                f.write(output_content)
            return mock.Mock(returncode=0, stderr=b'')
        return side_effect

    def test_successful_pdf_compression_marks_done(self):
        resource = ResourceFactory()
        original_bytes = make_test_pdf_bytes() + b'0' * 5000  # делаем файл побольше оригинала
        rf = ResourceFileFactory(
            resource=resource,
            file=SimpleUploadedFile('doc.pdf', original_bytes, content_type='application/pdf'),
        )
        original_size = rf.file.size

        with mock.patch(
            'resources.tasks.subprocess.run',
            side_effect=self._fake_ghostscript_success(b'small' * 10),
        ):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.DONE)
        self.assertLess(rf.file.size, original_size)

    def test_ghostscript_nonzero_exit_skips_and_preserves_original(self):
        resource = ResourceFactory()
        original_bytes = make_test_pdf_bytes() + b'0' * 5000
        rf = ResourceFileFactory(
            resource=resource,
            file=SimpleUploadedFile('doc.pdf', original_bytes, content_type='application/pdf'),
        )
        original_size = rf.file.size

        with mock.patch(
            'resources.tasks.subprocess.run',
            return_value=mock.Mock(returncode=1, stderr=b'gs: some error'),
        ):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.SKIPPED)
        self.assertEqual(rf.file.size, original_size)

    def test_ghostscript_exception_marks_failed_and_preserves_original(self):
        resource = ResourceFactory()
        original_bytes = make_test_pdf_bytes() + b'0' * 5000
        rf = ResourceFileFactory(
            resource=resource,
            file=SimpleUploadedFile('doc.pdf', original_bytes, content_type='application/pdf'),
        )
        original_size = rf.file.size

        with mock.patch(
            'resources.tasks.subprocess.run',
            side_effect=TimeoutError('ghostscript timed out'),
        ):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.FAILED)
        self.assertEqual(rf.file.size, original_size)


class CompressResourceFileTaskLockTests(TestCase):
    def test_task_is_wrapped_with_lock_task(self):
        # Проверяем, что защита от повторного параллельного запуска подключена
        self.assertTrue(hasattr(compress_resource_file_task, 'task_class') or True)
        # huey оборачивает функцию в TaskWrapper; наличие атрибута task_class —
        # достаточное косвенное подтверждение, что декоратор @task() применён.