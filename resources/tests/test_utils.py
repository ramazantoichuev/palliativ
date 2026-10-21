from django.test import SimpleTestCase

from resources.utils import file_kind
from resources.constants import (
    RESOURCE_SUBCATEGORY_MORE_THRESHOLD as THRESHOLD,
    RESOURCE_SUBCATEGORY_VISIBLE as VISIBLE,
)
from resources.utils import split_visible_hidden

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

def _items(n):
    return [(f"v{i}", f"L{i}") for i in range(n)]


class SplitVisibleHiddenTests(SimpleTestCase):
    def test_threshold_shows_all(self):
        shown, hidden = split_visible_hidden(_items(THRESHOLD))
        self.assertEqual(len(shown), THRESHOLD)
        self.assertEqual(hidden, [])

    def test_above_threshold_splits(self):
        shown, hidden = split_visible_hidden(_items(THRESHOLD + 1))
        self.assertEqual(len(shown), VISIBLE)
        self.assertEqual(len(hidden), THRESHOLD + 1 - VISIBLE)

    def test_active_hidden_replaces_last_visible(self):
        items = _items(THRESHOLD + 1)
        active = items[-1][0]
        shown, hidden = split_visible_hidden(items, active)
        self.assertEqual(shown[-1][0], active)
        self.assertEqual(len(shown), VISIBLE)
        self.assertIn(items[VISIBLE - 1], hidden)
        self.assertNotIn(items[-1], hidden)