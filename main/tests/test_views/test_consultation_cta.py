from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class TestConsultationCta(TestCase):
    """Быстрый доступ к форме консультации: кнопка в шапке и CTA на главной."""

    @classmethod
    def setUpTestData(cls):
        cls.consultation_url = reverse("main:new-consultation")

    def test_header_contains_consultation_button_on_any_page(self):
        response = self.client.get(reverse("main:about"))

        # Блок управления в шапке выводится дважды: десктопная
        # и мобильная версии (Ticket 118).
        self.assertContains(response, f'href="{self.consultation_url}"', count=2)
        self.assertContains(response, "Оставить заявку")

    def test_home_has_header_and_banner_links_but_not_middle_block_duplicate(self):
        """На главной точки входа: шапка (две версии, десктоп и мобильная,
        Ticket 118) и CTA-баннер; дублирующая кнопка из среднего блока убрана."""
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, f'href="{self.consultation_url}"', count=3)
        self.assertContains(response, "Нужна помощь или консультация?")

    def test_cta_text_is_unified_on_contacts_page(self):
        response = self.client.get(reverse("main:contacts"))

        self.assertContains(response, "Нужна консультация?")
        self.assertContains(response, "Мы свяжемся с вами")
        self.assertContains(response, "Оставить заявку")

    def test_language_switcher_is_pills_not_dropdown(self):
        """С Ticket 103 переключатель языка — «таблетки» RU/KY/EN,
        dropdown из Ticket 77 убран по Figma-референсу."""
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, "navbar-pill")
        self.assertNotContains(response, "dropdown-toggle")

    def test_navbar_is_sticky(self):
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, "sticky-top")

    def test_language_switch_still_works(self):
        # LocaleMiddleware активирует en на весь поток; без отката язык
        # утекает в следующие тесты (порядко-зависимые падения)
        self.addCleanup(translation.activate, "ru")

        response = self.client.post(
            reverse("set_language"),
            {"language": "en", "next": "/"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submit a request")
