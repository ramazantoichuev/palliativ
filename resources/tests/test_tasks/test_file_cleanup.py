import shutil
import tempfile
from unittest import mock

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings

from resources.models.resources import ResourceFile
from resources.tasks import delete_file_task
from resources.tests.factories import ResourceFactory

TMP_MEDIA = tempfile.mkdtemp()
TEST_OVERRIDES = dict(
    MIN_RESOURCE_FILE_SIZE_FOR_COMPRESSION_MB=0.001,  # ~1 КБ
    MAX_IMAGE_DIMENSION_PX=10,  # заставляет реальные тестовые картинки ресайзиться
)

@override_settings(**TEST_OVERRIDES, MEDIA_ROOT=TMP_MEDIA)
class ResourceFileCleanupTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        sync_delete = delete_file_task.call_local
        patcher = mock.patch("resources.tasks.delete_file_task", new=sync_delete)
        patcher.start()
        self.addCleanup(patcher.stop)
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