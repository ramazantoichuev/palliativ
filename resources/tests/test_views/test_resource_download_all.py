import io
import os
import tempfile
import zipfile

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from common.choices import ImageProcessingStatus
from resources.models.resources import ResourceFile
from resources.tests.factories import ResourceFactory


def make_pdf_file(resource, name="doc.pdf", content=b"%PDF-1.4 plain"):
    return ResourceFile.objects.create(
        resource=resource,
        file=SimpleUploadedFile(name, content, content_type="application/pdf"),
    )


def make_pending_word_file(resource, name="draft.docx"):
    rf = ResourceFile.objects.create(
        resource=resource,
        file=SimpleUploadedFile(name, b"word-bytes", content_type="application/octet-stream"),
    )
    ResourceFile.objects.filter(pk=rf.pk).update(
        processing_status=ImageProcessingStatus.PENDING
    )
    rf.refresh_from_db()
    return rf


def make_converted_word_file(resource, name="guide.docx", pdf_content=b"%PDF-1.4 converted"):
    """Word-файл с готовой PDF-версией, как после задачи Ticket 92."""
    rf = make_pending_word_file(resource, name=name)
    base_name = os.path.splitext(os.path.basename(name))[0]
    rf.converted_pdf.save(f"{base_name}.pdf", ContentFile(pdf_content), save=False)
    ResourceFile.objects.filter(pk=rf.pk).update(
        converted_pdf=rf.converted_pdf.name,
        processing_status=ImageProcessingStatus.DONE,
    )
    rf.refresh_from_db()
    return rf


def read_zip(response):
    return zipfile.ZipFile(io.BytesIO(response.content))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ResourceFilesZipViewTest(TestCase):
    def setUp(self):
        self.resource = ResourceFactory()
        self.url = reverse(
            "resources:resource_download_all", kwargs={"slug": self.resource.slug}
        )

    def test_zip_contains_all_files_with_readable_names(self):
        make_pdf_file(self.resource, name="alpha.pdf", content=b"%PDF-1.4 alpha")
        make_pdf_file(self.resource, name="beta.pdf", content=b"%PDF-1.4 beta")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn(
            f'attachment; filename="{self.resource.slug}.zip"',
            response["Content-Disposition"],
        )
        with read_zip(response) as archive:
            self.assertEqual(sorted(archive.namelist()), ["alpha.pdf", "beta.pdf"])
            self.assertEqual(archive.read("alpha.pdf"), b"%PDF-1.4 alpha")
            self.assertEqual(archive.read("beta.pdf"), b"%PDF-1.4 beta")

    def test_converted_word_goes_into_zip_as_pdf(self):
        make_pdf_file(self.resource, name="plain.pdf")
        make_converted_word_file(
            self.resource, name="guide.docx", pdf_content=b"%PDF-1.4 converted"
        )

        response = self.client.get(self.url)

        with read_zip(response) as archive:
            self.assertEqual(sorted(archive.namelist()), ["guide.pdf", "plain.pdf"])
            self.assertEqual(archive.read("guide.pdf"), b"%PDF-1.4 converted")

    def test_unprocessed_word_is_skipped_without_breaking_zip(self):
        make_pdf_file(self.resource, name="visible.pdf")
        make_pending_word_file(self.resource, name="draft.docx")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        with read_zip(response) as archive:
            self.assertEqual(archive.namelist(), ["visible.pdf"])

    def test_duplicate_names_get_numeric_suffix(self):
        # Оригинальный report.pdf и PDF-версия report.docx дают одинаковые имена
        make_pdf_file(self.resource, name="report.pdf")
        make_converted_word_file(self.resource, name="report.docx")

        response = self.client.get(self.url)

        with read_zip(response) as archive:
            self.assertEqual(
                sorted(archive.namelist()), ["report-1.pdf", "report.pdf"]
            )

    def test_resource_without_public_files_returns_404(self):
        make_pending_word_file(self.resource)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_resource_without_files_returns_404(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_nonexistent_slug_returns_404(self):
        url = reverse(
            "resources:resource_download_all", kwargs={"slug": "non-existent-slug"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DownloadAllButtonTest(TestCase):
    """Кнопка «Скачать все файлы (ZIP)» видна только при 2+ доступных файлах."""

    def setUp(self):
        self.resource = ResourceFactory()
        self.detail_url = reverse(
            "resources:resource_detail", kwargs={"slug": self.resource.slug}
        )
        self.download_url = reverse(
            "resources:resource_download_all", kwargs={"slug": self.resource.slug}
        )

    def test_button_shown_with_two_public_files(self):
        make_pdf_file(self.resource, name="alpha.pdf")
        make_pdf_file(self.resource, name="beta.pdf")

        response = self.client.get(self.detail_url)

        self.assertContains(response, self.download_url)

    def test_button_hidden_with_single_file(self):
        make_pdf_file(self.resource)

        response = self.client.get(self.detail_url)

        self.assertNotContains(response, self.download_url)

    def test_button_hidden_without_files(self):
        response = self.client.get(self.detail_url)

        self.assertNotContains(response, self.download_url)

    def test_button_hidden_when_second_file_is_not_public(self):
        make_pdf_file(self.resource)
        make_pending_word_file(self.resource)

        response = self.client.get(self.detail_url)

        self.assertNotContains(response, self.download_url)
