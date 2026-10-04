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
        self.assertTrue(reloaded.is_deleted)  # восстановление не произошло
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("Не удалось восстановить" in m for m in messages))

    def test_slug_is_readonly_when_editing_existing_block(self):
        block = EditableTextBlock.objects.create(slug="immutable_slug", content_ru="Текст")

        response = self.client.get(
            reverse("admin:main_editabletextblock_change", args=[block.pk]),
            SERVER_NAME="127.0.0.1",
        )

        self.assertNotContains(response, 'name="slug"')

    def test_slug_is_editable_when_creating_new_block(self):
        response = self.client.get(
            reverse("admin:main_editabletextblock_add"),
            SERVER_NAME="127.0.0.1",
        )

        self.assertContains(response, 'name="slug"')