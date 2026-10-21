from django.core.files.base import ContentFile
from django.test import TestCase

from resources.models.resources import ResourceFile
from resources.tests.factories import ResourceFactory
from resources.tests.mixins import MediaCleanupTestMixin


class ResourceDetailFilesTests(MediaCleanupTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.resource = ResourceFactory()

    def _add_file(self, name):
        return ResourceFile.objects.create(
            resource=self.resource, file=ContentFile(b"x", name)
        )

    def _get(self):
        return self.client.get(self.resource.get_absolute_url())

    def test_file_has_name_link_and_download_button(self):
        rf = self._add_file("guide.pdf")
        response = self._get()
        self.assertContains(response, 'class="file-row"', count=1)
        self.assertContains(response, 'target="_blank" rel="noopener"')
        self.assertContains(response, " download")
        self.assertContains(response, rf.public_file.url)

    def test_unconverted_word_is_hidden(self):
        self._add_file("doc.docx")
        response = self._get()
        self.assertNotContains(response, 'class="file-row"')

    def test_zip_only_with_two_or_more_files(self):
        self._add_file("a.pdf")
        zip_url = f"/resources/{self.resource.slug}/download/"
        response = self._get()
        self.assertNotContains(response, "ZIP")
        self._add_file("b.pdf")
        response = self._get()
        self.assertContains(response, "ZIP")