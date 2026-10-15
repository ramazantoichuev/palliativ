from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from main.models.editable_text_block import EditableTextBlock

User = get_user_model()


class EditableTextBlockAdminTests(TestCase):
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_superuser(
            username="admin_blocks", email="admin_blocks@test.kg", password="AdminPass123"
        )
        self.client.force_login(self.admin_user)

    def test_admin_changelist_shows_soft_deleted_records(self):
        block = EditableTextBlock.objects.create(slug="visible_deleted", content_ru="Текст")
        block.soft_delete()

        response = self.client.get(reverse("admin:main_editabletextblock_changelist"))

        self.assertContains(response, "visible_deleted")

    def test_delete_single_object_soft_deletes_instead_of_removing_row(self):
        block = EditableTextBlock.objects.create(slug="to_delete", content_ru="Текст")

        self.client.post(
            reverse("admin:main_editabletextblock_delete", args=[block.pk]),
            data={"post": "yes"},
        )

        reloaded = EditableTextBlock.all_objects.get(pk=block.pk)
        self.assertTrue(reloaded.is_deleted)

    def test_bulk_delete_action_soft_deletes_selected_objects(self):
        block1 = EditableTextBlock.objects.create(slug="bulk_1", content_ru="Текст 1")
        block2 = EditableTextBlock.objects.create(slug="bulk_2", content_ru="Текст 2")

        self.client.post(
            reverse("admin:main_editabletextblock_changelist"),
            data={
                "action": "delete_selected",
                "_selected_action": [block1.pk, block2.pk],
                "post": "yes",
            },
        )

        self.assertTrue(EditableTextBlock.all_objects.get(pk=block1.pk).is_deleted)
        self.assertTrue(EditableTextBlock.all_objects.get(pk=block2.pk).is_deleted)

    def test_restore_action_clears_is_deleted(self):
        block = EditableTextBlock.objects.create(slug="to_restore", content_ru="Текст")
        block.soft_delete()

        response = self.client.post(
            reverse("admin:main_editabletextblock_changelist"),
            data={
                "action": "restore_selected",
                "_selected_action": [block.pk],
            },
            follow=True,
            SERVER_NAME="127.0.0.1",
        )

        reloaded = EditableTextBlock.objects.get(pk=block.pk)
        self.assertFalse(reloaded.is_deleted)
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("Восстановлено" in m for m in messages))

    def test_restore_fails_gracefully_when_slug_taken_by_active_block(self):
        deleted_block = EditableTextBlock.objects.create(slug="conflict_slug", content_ru="Старый")
        deleted_block.soft_delete()
        EditableTextBlock.objects.create(slug="conflict_slug", content_ru="Новый активный")

        response = self.client.post(
            reverse("admin:main_editabletextblock_changelist"),
            data={
                "action": "restore_selected",
                "_selected_action": [deleted_block.pk],
            },
            follow=True,
            SERVER_NAME="127.0.0.1",
        )

        reloaded = EditableTextBlock.all_objects.get(pk=deleted_block.pk)
        self.assertTrue(reloaded.is_deleted)
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("Не удалось восстановить" in m for m in messages))

    def test_slug_is_readonly_when_editing_existing_block(self):
        block = EditableTextBlock.objects.create(slug="immutable_slug", content_ru="Текст")

        response = self.client.get(
            reverse("admin:main_editabletextblock_change", args=[block.pk]),
            SERVER_NAME="127.0.0.1",
        )

        self.assertNotContains(response, 'name="slug"')

    def test_add_page_returns_403(self):
        response = self.client.get(
            reverse("admin:main_editabletextblock_add"),
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 403)

    def test_add_button_is_not_displayed(self):
        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Добавить")

    def test_post_to_add_page_does_not_create_block(self):
        response = self.client.post(
            reverse("admin:main_editabletextblock_add"),
            data={
                "slug": "new_test_block",
                "content_ru": "Новый текст",
            },
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            EditableTextBlock.all_objects.filter(
                slug="new_test_block"
            ).exists()
        )


    def test_page_filter_home_shows_only_home_blocks(self):
        EditableTextBlock.objects.create(slug="home_title", content_ru="Главная")
        EditableTextBlock.objects.create(slug="about_title", content_ru="О нас")

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"page": "home"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home_title")
        self.assertNotContains(response, "about_title")

    def test_page_filter_about_shows_only_about_blocks(self):
        EditableTextBlock.objects.create(slug="home_title", content_ru="Главная")
        EditableTextBlock.objects.create(slug="about_title", content_ru="О нас")

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"page": "about"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "about_title")
        self.assertNotContains(response, "home_title")

    def test_page_filter_without_value_shows_all_blocks(self):
        EditableTextBlock.objects.create(slug="home_title", content_ru="Главная")
        EditableTextBlock.objects.create(slug="about_title", content_ru="О нас")

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home_title")
        self.assertContains(response, "about_title")

    def test_page_filter_unknown_value_shows_all_blocks(self):
        EditableTextBlock.objects.create(slug="home_title", content_ru="Главная")
        EditableTextBlock.objects.create(slug="about_title", content_ru="О нас")

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"page": "unknown"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home_title")
        self.assertContains(response, "about_title")

    def test_page_filter_includes_soft_deleted_blocks(self):
        block = EditableTextBlock.objects.create(
            slug="home_deleted_title",
            content_ru="Удалённый блок",
        )
        block.soft_delete()

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"page": "home"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home_deleted_title")

    def test_search_finds_block_by_slug(self):
        EditableTextBlock.objects.create(
            slug="home_unique_title",
            content_ru="Текст",
        )

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"q": "unique_title"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home_unique_title")

    def test_search_finds_block_by_content(self):
        EditableTextBlock.objects.create(
            slug="home_search_test",
            content_ru="УникальныйПоисковыйТекст",
        )

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"q": "УникальныйПоисковыйТекст"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home_search_test")

    def test_search_with_no_matches_returns_empty_list(self):
        EditableTextBlock.objects.create(
            slug="home_existing_block",
            content_ru="Существующий текст",
        )

        response = self.client.get(
            reverse("admin:main_editabletextblock_changelist"),
            {"q": "no_such_block_987654"},
            SERVER_NAME="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "home_existing_block")