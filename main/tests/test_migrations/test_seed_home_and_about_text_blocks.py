import importlib

from django.test import TestCase

from main.models.editable_text_block import EditableTextBlock

_migration = importlib.import_module(
    "main.migrations.0009_seed_home_and_about_text_blocks"
)
TEXT_BLOCKS = _migration.TEXT_BLOCKS


class SeedHomeAndAboutTextBlocksMigrationTest(TestCase):
    """
    Тестовая БД создаётся через полный прогон миграций, поэтому на момент
    запуска тестов data-миграция 0009 уже применена — проверяем её результат
    напрямую через модель, не поднимая отдельный MigrationExecutor.
    """

    def test_all_expected_slugs_exist_with_non_empty_content(self):
        for slug in TEXT_BLOCKS:
            with self.subTest(slug=slug):
                block = EditableTextBlock.objects.get(slug=slug)
                self.assertTrue(block.content.strip())