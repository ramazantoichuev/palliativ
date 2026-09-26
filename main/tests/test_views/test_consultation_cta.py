from django.test import TestCase
from django.urls import reverse


class TestConsultationCta(TestCase):
    """Быстрый доступ к форме консультации: кнопка в шапке и CTA на главной."""

    @classmethod
    def setUpTestData(cls):
        cls.consultation_url = reverse("main:new-consultation")

    def test_header_contains_consultation_button_on_any_page(self):
        response = self.client.get(reverse("main:about"))

        self.assertContains(response, f'href="{self.consultation_url}"', count=1)
        self.assertContains(response, "Оставить заявку")

    def test_home_has_header_and_banner_links_but_not_middle_block_duplicate(self):
        """На главной ровно две точки входа: шапка и CTA-баннер —
        дублирующая кнопка из среднего блока убрана."""
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, f'href="{self.consultation_url}"', count=2)
        self.assertContains(response, "Нужна помощь или консультация?")

    def test_cta_text_is_unified_on_contacts_page(self):
        response = self.client.get(reverse("main:contacts"))

        self.assertNotContains(response, "Нужна консультация")
        self.assertContains(response, "Оставить заявку")

    def test_language_switcher_is_dropdown_not_button_group(self):
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, "dropdown-menu")
        self.assertNotContains(response, "btn-group")

    def test_navbar_is_sticky(self):
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, "sticky-top")

    def test_language_switch_still_works(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "en", "next": "/"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submit a request")
