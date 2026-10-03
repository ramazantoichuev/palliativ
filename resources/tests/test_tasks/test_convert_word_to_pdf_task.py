import os
import shutil
import unittest
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from common.choices import ImageProcessingStatus
from resources.models.resources import ResourceFile
from resources.tasks import compress_resource_file_task
from resources.tests.factories import ResourceFactory


def make_docx_resource_file(resource, name="guide.docx"):
    return ResourceFile.objects.create(
        resource=resource,
        file=SimpleUploadedFile(name, b"word-bytes", content_type="application/octet-stream"),
    )


def soffice_success(*args, **kwargs):
    """Имитирует soffice: кладёт PDF в --outdir и возвращает код 0."""
    command = args[0]
    out_dir = command[command.index("--outdir") + 1]
    source = command[-1]
    base_name = os.path.splitext(os.path.basename(source))[0]
    with open(os.path.join(out_dir, f"{base_name}.pdf"), "wb") as pdf:
        pdf.write(b"%PDF-1.4 fake")
    return mock.Mock(returncode=0, stderr=b"")


class ConvertWordEnqueueTests(TestCase):
    def test_docx_save_enqueues_processing(self):
        resource = ResourceFactory()

        with mock.patch("resources.tasks.compress_resource_file_task") as mocked_task:
            with self.captureOnCommitCallbacks(execute=True):
                rf = make_docx_resource_file(resource)

        mocked_task.assert_called_once_with(rf.pk)
        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.PENDING)


class ConvertWordSuccessTests(TestCase):
    def test_successful_conversion_sets_converted_pdf_and_done(self):
        rf = make_docx_resource_file(ResourceFactory())

        with mock.patch(
            "resources.tasks.subprocess.run", side_effect=soffice_success
        ) as mocked_run:
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.DONE)
        self.assertTrue(rf.converted_pdf)
        self.assertTrue(rf.converted_pdf.name.startswith("resources/files/converted/"))
        self.assertTrue(rf.converted_pdf.name.endswith(".pdf"))
        self.assertTrue(rf.file)  # оригинальный Word сохранён

        command = mocked_run.call_args.args[0]
        self.assertEqual(command[0], "soffice")
        self.assertIn("--headless", command)

    def test_doc_extension_is_converted_too(self):
        rf = make_docx_resource_file(ResourceFactory(), name="old-format.doc")

        with mock.patch("resources.tasks.subprocess.run", side_effect=soffice_success):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.DONE)
        self.assertTrue(rf.converted_pdf)


class ConvertWordFailureTests(TestCase):
    def test_soffice_error_marks_failed_and_keeps_original(self):
        rf = make_docx_resource_file(ResourceFactory())

        with mock.patch(
            "resources.tasks.subprocess.run",
            return_value=mock.Mock(returncode=1, stderr=b"boom"),
        ):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.FAILED)
        self.assertFalse(rf.converted_pdf)
        self.assertTrue(rf.file)
        with rf.file.open("rb") as f:
            self.assertEqual(f.read(), b"word-bytes")

    def test_soffice_timeout_marks_failed(self):
        import subprocess

        rf = make_docx_resource_file(ResourceFactory())

        with mock.patch(
            "resources.tasks.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="soffice", timeout=1),
        ):
            compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.FAILED)
        self.assertFalse(rf.converted_pdf)


class WordFileVisibilityTests(TestCase):
    """Посетитель видит только готовую PDF-версию Word-файла."""

    def setUp(self):
        self.resource = ResourceFactory()
        self.url = reverse(
            "resources:resource_detail", kwargs={"slug": self.resource.slug}
        )

    def test_converted_word_is_shown_as_pdf(self):
        rf = make_docx_resource_file(self.resource)
        with mock.patch("resources.tasks.subprocess.run", side_effect=soffice_success):
            compress_resource_file_task.call_local(rf.pk)

        response = self.client.get(self.url)
        rf.refresh_from_db()

        self.assertContains(response, rf.converted_pdf.url)
        self.assertNotContains(response, rf.file.url)

    def test_pending_word_is_hidden_from_visitor(self):
        rf = make_docx_resource_file(self.resource)
        ResourceFile.objects.filter(pk=rf.pk).update(
            processing_status=ImageProcessingStatus.PENDING
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, rf.file.url)

    def test_failed_word_is_hidden_from_visitor(self):
        rf = make_docx_resource_file(self.resource)
        ResourceFile.objects.filter(pk=rf.pk).update(
            processing_status=ImageProcessingStatus.FAILED
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, rf.file.url)

    def test_plain_pdf_is_shown_as_before(self):
        rf = ResourceFile.objects.create(
            resource=self.resource,
            file=SimpleUploadedFile("plain.pdf", b"%PDF-1.4", content_type="application/pdf"),
        )

        response = self.client.get(self.url)

        self.assertContains(response, rf.file.url)


@unittest.skipUnless(
    shutil.which("soffice"), "LibreOffice (soffice) не установлен — smoke пропущен"
)
class ConvertWordRealSofficeSmokeTests(TestCase):
    """Интеграционный smoke с настоящим soffice.

    Выполняется только там, где установлен LibreOffice (docker-образ,
    локальная машина разработчика); в остальных окружениях пропускается,
    так что требование тикета «в тестах процесс не запускается» для CI
    сохраняется.
    """

    def test_real_docx_converts_to_valid_pdf(self):
        import zipfile
        from io import BytesIO

        # Минимальный валидный .docx собираем на лету (zip с OOXML-структурой)
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
            )
            z.writestr(
                "_rels/.rels",
                '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
            )
            z.writestr(
                "word/document.xml",
                '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>Смоук-тест Ticket 92: кириллица — Бишкек.</w:t></w:r></w:p></w:body></w:document>",
            )

        rf = ResourceFile.objects.create(
            resource=ResourceFactory(),
            file=SimpleUploadedFile("real-smoke.docx", buf.getvalue()),
        )

        compress_resource_file_task.call_local(rf.pk)

        rf.refresh_from_db()
        self.assertEqual(rf.processing_status, ImageProcessingStatus.DONE)
        with rf.converted_pdf.open("rb") as f:
            self.assertEqual(f.read(5), b"%PDF-")
