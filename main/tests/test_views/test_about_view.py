from django.test import TestCase
from django.urls import reverse

from main.models.editable_text_block import EditableTextBlock


class AboutViewTest(TestCase):

    def setUp(self):
        self.url = reverse("main:about")

    def test_about_page_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_heading_renders_from_fallback_when_no_db_record(self):
        EditableTextBlock.objects.filter(slug="about_page_title").delete()

        response = self.client.get(self.url)

        self.assertContains(response, "Об Ассоциации")

    def test_heading_renders_from_db_when_present(self):
        EditableTextBlock.objects.update_or_create(
            slug="about_page_title",
            defaults={"content": "Кастомный заголовок страницы"},
        )

        response = self.client.get(self.url)

        self.assertContains(response, "Кастомный заголовок страницы")

    def test_page_does_not_break_when_record_deleted(self):
        EditableTextBlock.objects.filter(slug="about_page_title").delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Об Ассоциации")