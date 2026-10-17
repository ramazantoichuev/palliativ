from django.test import SimpleTestCase

from resources.utils import file_kind


class FileKindTests(SimpleTestCase):
    def test_pdf(self):
        self.assertEqual(file_kind("a.pdf"), "pdf")

    def test_images(self):
        for name in ("a.jpg", "a.jpeg", "a.png", "a.webp"):
            self.assertEqual(file_kind(name), "image")

    def test_unknown_extension(self):
        self.assertEqual(file_kind("a.xyz"), "other")

    def test_case_insensitive(self):
        self.assertEqual(file_kind("A.PDF"), "pdf")
        self.assertEqual(file_kind("photo.JPG"), "image")

    def test_no_extension(self):
        self.assertEqual(file_kind("readme"), "other")