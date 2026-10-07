from django.test import TestCase
from django.urls import reverse


class DarkNavbarTests(TestCase):
    """Тёмный навбар и переключатель языка «таблетками» (Ticket 103)."""

    def test_navbar_uses_dark_brand_background(self):
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, 'navbar navbar-expand-lg bg-dark')
        self.assertNotContains(response, "navbar-light bg-white")

    def test_language_pills_rendered_for_all_languages(self):
        response = self.client.get(reverse("main:home"))
        html = response.content.decode()

        for code in ("ru", "ky", "en"):
            self.assertIn(f'name="language" value="{code}"', html)
        # активный язык (ru по умолчанию) выделен
        self.assertContains(response, "navbar-pill active")
        self.assertContains(response, 'aria-current="true"')

    def test_dropdown_markup_removed(self):
        response = self.client.get(reverse("main:home"))

        self.assertNotContains(response, "dropdown-toggle")
