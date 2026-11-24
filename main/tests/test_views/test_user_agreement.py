from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from main.models.editable_text_block import EditableTextBlock
from main.models.site_contacts import SiteContacts
from main.user_agreement import USER_AGREEMENT_SLUGS


def create_blocks(skip=(), **overrides):
    """Задаёт тексты блоков соглашения (их создаёт миграция 0014).

    Текст каждого блока — «Текст <slug>», блоки из skip становятся пустыми.
    """
    for slug in USER_AGREEMENT_SLUGS:
        text = "" if slug in skip else overrides.get(slug, f"Текст {slug}")
        EditableTextBlock.objects.filter(slug=slug).update(content_ru=text)


def empty_blocks():
    create_blocks(skip=USER_AGREEMENT_SLUGS)


class TestUserAgreementPublication(TestCase):
    """Страница и ссылка в футере появляются, только когда весь текст внесён."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("main:user_agreement")

    def test_page_is_not_found_while_blocks_are_empty(self):
        empty_blocks()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_page_is_not_found_when_one_block_is_empty(self):
        create_blocks(skip=("user-agreement-law",))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_page_is_not_found_when_one_block_is_blank(self):
        create_blocks(**{"user-agreement-ip": "   "})

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_page_is_not_found_when_one_block_is_deleted(self):
        create_blocks()
        EditableTextBlock.objects.get(slug="user-agreement-ip").delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_page_is_not_found_when_one_block_is_soft_deleted(self):
        create_blocks()
        EditableTextBlock.objects.get(slug="user-agreement-ip").soft_delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_migration_creates_all_blocks_with_agreed_text(self):
        texts = dict(
            EditableTextBlock.objects.filter(slug__in=USER_AGREEMENT_SLUGS)
            .values_list("slug", "content_ru")
        )

        self.assertEqual(set(texts), set(USER_AGREEMENT_SLUGS))
        self.assertTrue(all(text.strip() for text in texts.values()))

    def test_agreed_text_is_published_right_after_migration(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Используя сайт")
        self.assertContains(response, "Редакция от: 20 октября 2026 г.")

    def test_footer_link_is_hidden_until_text_is_complete(self):
        create_blocks(skip=("user-agreement-law",))

        response = self.client.get(reverse("main:home"))

        self.assertNotContains(response, f'href="{self.url}"')

    def test_page_opens_when_all_blocks_are_filled(self):
        create_blocks()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/user_agreement.html")

    def test_footer_link_is_shown_when_text_is_complete(self):
        create_blocks()

        response = self.client.get(reverse("main:home"))

        self.assertContains(response, f'href="{self.url}"')


class TestUserAgreementContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("main:user_agreement")

    def test_page_shows_headings_and_block_texts(self):
        create_blocks()

        response = self.client.get(self.url)

        for heading in (
            "Пользовательское соглашение",
            "1. Общие положения",
            "2. Характер Сайта",
            "3. Права и обязанности пользователя",
            "4. Интеллектуальная собственность",
            "5. Ограничение ответственности",
            "6. Изменение Соглашения и материалов",
            "7. Применимое право",
        ):
            self.assertContains(response, heading)
        for slug in USER_AGREEMENT_SLUGS:
            self.assertContains(response, f"Текст {slug}")

    def test_html_typed_in_admin_is_escaped(self):
        create_blocks(**{"user-agreement-law": "<script>alert(1)</script>"})

        response = self.client.get(self.url)

        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_bullet_lines_stay_in_one_paragraph(self):
        create_blocks(**{"user-agreement-duties": "• первый;\n• второй."})

        response = self.client.get(self.url)

        self.assertContains(response, "<p>• первый;<br>• второй.</p>", html=True)

    def test_contacts_come_from_site_settings(self):
        create_blocks()
        SiteContacts.objects.update_or_create(
            pk=1,
            defaults={
                "phone": "+996312214015",
                "phone_display": "+996 312 21 40 15",
                "email": "info@example.kg",
                "address": "Ул. Юдахина 61",
            },
        )

        response = self.client.get(self.url)

        self.assertContains(response, "info@example.kg")
        self.assertContains(response, "+996 312 21 40 15")
        self.assertContains(response, "Ул. Юдахина 61")

    def test_other_language_shows_russian_text_until_translation_is_added(self):
        create_blocks()

        response = self.client.get(self.url, headers={"accept-language": "ky"})

        self.assertContains(response, "Текст user-agreement-law")

    def test_other_language_shows_translation_once_client_adds_it(self):
        create_blocks()
        block = EditableTextBlock.objects.get(slug="user-agreement-law")
        block.content_en = "This Agreement is governed by the law of the Kyrgyz Republic."
        block.save()

        response = self.client.get(self.url, headers={"accept-language": "en"})

        self.assertContains(response, "governed by the law of the Kyrgyz Republic")
        self.assertNotContains(response, "Текст user-agreement-law")

    def test_footer_link_goes_through_translation(self):
        create_blocks()

        response = self.client.get(reverse("main:home"), headers={"accept-language": "en"})

        self.assertContains(response, "User Agreement")
        self.assertNotContains(response, "Пользовательское соглашение")


class TestUserAgreementPublishedTag(TestCase):

    @staticmethod
    def render():
        return Template(
            "{% load user_agreement %}"
            "{% user_agreement_published as published %}{{ published }}"
        ).render(Context())

    def test_false_while_blocks_are_empty(self):
        empty_blocks()

        self.assertEqual(self.render(), "False")

    def test_true_when_all_blocks_are_filled(self):
        create_blocks()

        self.assertEqual(self.render(), "True")
