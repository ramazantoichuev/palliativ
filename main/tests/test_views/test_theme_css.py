from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse


class ThemeCssTests(TestCase):
    """Брендовая палитра (Ticket 101) подключена и содержит переменные."""

    def test_theme_css_static_file_exists(self):
        path = finders.find("main/css/theme.css")
        self.assertIsNotNone(path)

    def test_theme_css_defines_brand_variables(self):
        path = finders.find("main/css/theme.css")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for variable in (
            "--mustard",
            "--deep-blue",
            "--soft-green",
            "--warm-gray",
            "--bg",
            "--text",
        ):
            self.assertIn(f"{variable}:", content)

    def test_theme_css_linked_after_bootstrap(self):
        response = self.client.get(reverse("main:home"))
        html = response.content.decode()

        bootstrap_position = html.find("bootstrap.min.css")
        theme_position = html.find("main/css/theme.css")

        self.assertNotEqual(bootstrap_position, -1)
        self.assertNotEqual(theme_position, -1)
        self.assertGreater(theme_position, bootstrap_position)
