from django.template import Context, Template
from django.test import TestCase
from django.utils import translation

from accounts.models import BaseUser
from main.models.editable_text_block import EditableTextBlock


def render_tag(tag):
    return Template("{% load text_blocks %}" + tag).render(Context())


class TestGetTextBlockTag(TestCase):

    def test_returns_block_content_from_db(self):
        EditableTextBlock.objects.create(slug="mission", content_ru="Наша миссия.")

        html = render_tag('{% get_text_block "mission" %}')

        self.assertIn("Наша миссия.", html)

    def test_fallback_is_rendered_when_block_is_missing(self):
        html = render_tag('{% get_text_block "missing" fallback="Запасной текст" %}')

        self.assertIn("Запасной текст", html)

    def test_returns_empty_string_without_block_and_fallback(self):
        self.assertEqual(render_tag('{% get_text_block "missing" %}'), "")

    def test_db_content_html_is_escaped(self):
        """Контент из админки не должен исполняться как HTML (stored XSS)."""
        EditableTextBlock.objects.create(
            slug="evil", content_ru="<script>alert(1)</script>текст"
        )

        html = render_tag('{% get_text_block "evil" %}')

        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("текст", html)

    def test_fallback_markup_is_trusted(self):
        html = render_tag(
            '{% get_text_block "missing" fallback="<ul><li>Пункт</li></ul>" %}'
        )

        self.assertIn("<li>Пункт</li>", html)

    def test_as_list_renders_lines_as_list_items_and_escapes(self):
        EditableTextBlock.objects.create(
            slug="values", content_ru="Первый\n<b>Второй</b>\n"
        )

        html = render_tag('{% get_text_block "values" as_list=True %}')

        self.assertIn("<ul><li>Первый</li><li>&lt;b&gt;Второй&lt;/b&gt;</li></ul>", html)

    def test_content_falls_back_to_russian_for_other_language(self):
        EditableTextBlock.objects.create(slug="mission", content_ru="Только по-русски.")

        with translation.override("en"):
            html = render_tag('{% get_text_block "mission" %}')

        self.assertIn("Только по-русски.", html)


class TestEditableTextBlockAdminAccess(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = "/admin/main/editabletextblock/"
        cls.manager = BaseUser.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="x",
            role=BaseUser.Role.MANAGER,
            is_staff=True,
            phone="+996700000001",
        )
        cls.doctor = BaseUser.objects.create_user(
            username="doctor",
            email="doctor@example.com",
            password="x",
            role=BaseUser.Role.DOCTOR,
            is_staff=True,
            phone="+996700000002",
        )

    def test_manager_can_open_blocks_list(self):
        self.client.force_login(self.manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_non_manager_staff_is_denied(self):
        self.client.force_login(self.doctor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
