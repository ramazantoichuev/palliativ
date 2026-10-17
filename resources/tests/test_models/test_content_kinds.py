from django.core.files.base import ContentFile
from django.test import TestCase

from resources.models.resources import ResourceFile, ResourceVideoLink
from resources.tests.factories import ResourceFactory
from resources.tests.mixins import MediaCleanupTestMixin


class ContentKindsTests(MediaCleanupTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.resource = ResourceFactory()

    def _add_file(self, name):
        return ResourceFile.objects.create(
            resource=self.resource, file=ContentFile(b"x", name)
        )

    def test_empty(self):
        self.assertEqual(self.resource.content_kinds, [])

    def test_only_files(self):
        self._add_file("a.pdf")
        self._add_file("b.jpg")
        self.assertEqual(self.resource.content_kinds, ["pdf", "image"])

    def test_only_video(self):
        ResourceVideoLink.objects.create(
            resource=self.resource, url="https://youtu.be/dQw4w9WgXcQ"
        )
        self.assertEqual(self.resource.content_kinds, ["video"])

    def test_mixed(self):
        self._add_file("a.pdf")
        ResourceVideoLink.objects.create(
            resource=self.resource, url="https://youtu.be/dQw4w9WgXcQ"
        )
        self.assertEqual(self.resource.content_kinds, ["pdf", "video"])

    def test_unconverted_word_is_hidden(self):
        self._add_file("a.docx")
        self.assertEqual(self.resource.content_kinds, [])