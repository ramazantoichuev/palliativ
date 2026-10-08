from unittest import mock

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings
from resources.tests.mixins import MediaCleanupTestMixin

from resources.models.resources import ResourceFile
from resources.tasks import delete_file_task
from resources.tests.factories import ResourceFactory

TEST_OVERRIDES = dict(
    MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB=0.001,  # ~1 КБ
    MAX_IMAGE_DIMENSION_PX=10,  # заставляет реальные тестовые картинки ресайзиться
)

@override_settings(**TEST_OVERRIDES)
class ResourceFileCleanupTests(MediaCleanupTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        for target in (
                'resources.tasks._compress_image',
                'resources.tasks._compress_pdf',
                'resources.tasks._convert_word_to_pdf',
        ):
            patcher = mock.patch(target, return_value=False)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.resource = ResourceFactory()

    def _create(self):
        return ResourceFile.objects.create(
            resource=self.resource,
            file=ContentFile(b"x", "a.pdf"),
        )

    def test_delete_removes_file(self):
        obj = self._create()
        path = obj.file.name
        self.assertTrue(default_storage.exists(path))
        with self.captureOnCommitCallbacks(execute=True):
            obj.delete()
        self.assertFalse(default_storage.exists(path))

    def test_replace_removes_old_keeps_new(self):
        obj = self._create()
        old = obj.file.name
        obj.file = ContentFile(b"y", "b.pdf")
        with self.captureOnCommitCallbacks(execute=True):
            obj.save()
        self.assertFalse(default_storage.exists(old))
        self.assertTrue(default_storage.exists(obj.file.name))

    def test_delete_removes_converted_pdf(self):
        obj = self._create()
        obj.converted_pdf.save("a_converted.pdf", ContentFile(b"%PDF-1.4"), save=True)
        main_path = obj.file.name
        pdf_path = obj.converted_pdf.name
        self.assertTrue(default_storage.exists(pdf_path))
        with self.captureOnCommitCallbacks(execute=True):
            obj.delete()
        self.assertFalse(default_storage.exists(main_path))
        self.assertFalse(default_storage.exists(pdf_path))

    def test_missing_file_does_not_raise(self):
        delete_file_task.call_local("nonexistent/path.pdf")

    def test_replace_removes_old_file_and_old_converted_pdf(self):
        obj = self._create()
        obj.converted_pdf.save("a_converted.pdf", ContentFile(b"%PDF-1.4"), save=True)
        old_file = obj.file.name
        old_pdf = obj.converted_pdf.name

        obj.file = ContentFile(b"y", "b.pdf")
        with self.captureOnCommitCallbacks(execute=True):
            obj.save()

        self.assertFalse(default_storage.exists(old_file))
        self.assertFalse(default_storage.exists(old_pdf))
        self.assertTrue(default_storage.exists(obj.file.name))

    def test_deleting_resource_removes_files_of_all_its_resource_files(self):
        first = self._create()
        second = self._create()
        paths = [first.file.name, second.file.name]
        for p in paths:
            self.assertTrue(default_storage.exists(p))

        with self.captureOnCommitCallbacks(execute=True):
            self.resource.delete()

        for p in paths:
            self.assertFalse(default_storage.exists(p))