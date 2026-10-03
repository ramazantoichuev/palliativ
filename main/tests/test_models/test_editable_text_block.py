from django.db import IntegrityError, transaction
from django.test import TestCase

from main.models.editable_text_block import EditableTextBlock


class EditableTextBlockSoftDeleteTests(TestCase):
    def test_soft_delete_sets_is_deleted_and_timestamp(self):
        block = EditableTextBlock.objects.create(slug="test_block", content_ru="Текст")

        block.soft_delete()

        reloaded = EditableTextBlock.all_objects.get(pk=block.pk)
        self.assertTrue(reloaded.is_deleted)
        self.assertIsNotNone(reloaded.deleted_at)

    def test_soft_deleted_block_not_in_default_manager(self):
        block = EditableTextBlock.objects.create(slug="test_block", content_ru="Текст")
        block.soft_delete()

        self.assertFalse(EditableTextBlock.objects.filter(pk=block.pk).exists())

    def test_soft_deleted_block_still_in_all_objects(self):
        block = EditableTextBlock.objects.create(slug="test_block", content_ru="Текст")
        block.soft_delete()

        self.assertTrue(EditableTextBlock.all_objects.filter(pk=block.pk).exists())

    def test_restore_clears_is_deleted_and_timestamp(self):
        block = EditableTextBlock.objects.create(slug="test_block", content_ru="Текст")
        block.soft_delete()

        block.restore()

        reloaded = EditableTextBlock.objects.get(pk=block.pk)
        self.assertFalse(reloaded.is_deleted)
        self.assertIsNone(reloaded.deleted_at)

    def test_row_physically_remains_in_database_after_soft_delete(self):
        block = EditableTextBlock.objects.create(slug="test_block", content_ru="Текст")
        block_pk = block.pk

        block.soft_delete()

        self.assertTrue(EditableTextBlock.all_objects.filter(pk=block_pk).exists())

    def test_new_active_block_can_reuse_slug_of_soft_deleted_block(self):
        old_block = EditableTextBlock.objects.create(slug="reused_slug", content_ru="Старый")
        old_block.soft_delete()

        new_block = EditableTextBlock.objects.create(slug="reused_slug", content_ru="Новый")

        self.assertTrue(EditableTextBlock.objects.filter(pk=new_block.pk).exists())

    def test_two_active_blocks_cannot_share_the_same_slug(self):
        EditableTextBlock.objects.create(slug="unique_slug", content_ru="Первый")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EditableTextBlock.objects.create(slug="unique_slug", content_ru="Второй")