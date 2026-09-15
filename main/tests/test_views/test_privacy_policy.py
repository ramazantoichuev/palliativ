from django.test import TestCase
from django.urls import reverse


class TestPrivacyPolicyView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("main:privacy_policy")

    def test_page_opens_and_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/privacy_policy.html")

    def test_page_shows_policy_sections(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Политика обработки персональных данных")
        self.assertContains(response, "Какие данные собираются")
        self.assertContains(response, "Цель обработки")
        self.assertContains(response, "Кто имеет доступ")

    def test_footer_contains_link_to_policy(self):
        response = self.client.get(reverse("main:home"))

        self.assertContains(response, f'href="{self.url}"')

    def test_consultation_page_contains_link_to_policy(self):
        response = self.client.get(reverse("main:new-consultation"))

        self.assertContains(response, f'href="{self.url}"')
        self.assertContains(response, "Отправляя форму, вы соглашаетесь с")

    def test_footer_link_goes_through_translation(self):
        """Название ссылки в футере не должно утекать по-русски при другом языке."""
        response = self.client.get(reverse("main:home"), headers={"accept-language": "en"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Data Processing Policy")
        self.assertNotContains(response, "Политика обработки данных")
