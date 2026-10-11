from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class RemoveTestBlockHeyMigrationTests(TransactionTestCase):
    migrate_from = ("main", "0012_alter_editabletextblock_slug_and_more")
    migrate_to = ("main", "0013_remove_test_block_hey")

    def setUp(self):
        super().setUp()

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])

        old_apps = executor.loader.project_state(
            [self.migrate_from]
        ).apps

        EditableTextBlock = old_apps.get_model(
            "main", "EditableTextBlock"
        )
        HistoricalEditableTextBlock = old_apps.get_model(
            "main", "HistoricalEditableTextBlock"
        )

        self.hey = EditableTextBlock.objects.create(
            slug="hey",
            content="Тестовый блок",
        )
        self.other = EditableTextBlock.objects.create(
            slug="keep_me",
            content="Обычный блок",
        )

        self.create_history(
            HistoricalEditableTextBlock,
            self.hey,
        )
        self.create_history(
            HistoricalEditableTextBlock,
            self.other,
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])

        self.apps = MigrationExecutor(connection).loader.project_state([self.migrate_to]).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def create_history(self, HistoricalModel, block):
        values = {}

        for field in HistoricalModel._meta.concrete_fields:
            if field.name == "history_id":
                continue

            if field.name == "history_date":
                values[field.attname] = timezone.now()
            elif field.name == "history_type":
                values[field.attname] = "+"
            elif field.name in ("history_change_reason", "history_user"):
                values[field.attname] = None
            elif hasattr(block, field.attname):
                values[field.attname] = getattr(block, field.attname)
            elif field.has_default() or field.null:
                continue
            else:
                raise AssertionError(
                    f"Неизвестное обязательное поле истории: {field.name}"
                )

        return HistoricalModel.objects.create(**values)

    def test_migration_removes_hey_and_its_history(self):
        EditableTextBlock = self.apps.get_model(
            "main", "EditableTextBlock"
        )
        HistoricalEditableTextBlock = self.apps.get_model(
            "main", "HistoricalEditableTextBlock"
        )

        self.assertFalse(
            EditableTextBlock.objects.filter(slug="hey").exists()
        )
        self.assertFalse(
            HistoricalEditableTextBlock.objects.filter(
                slug="hey"
            ).exists()
        )

    def test_migration_preserves_other_blocks_and_history(self):
        EditableTextBlock = self.apps.get_model(
            "main", "EditableTextBlock"
        )
        HistoricalEditableTextBlock = self.apps.get_model(
            "main", "HistoricalEditableTextBlock"
        )

        self.assertTrue(
            EditableTextBlock.objects.filter(slug="keep_me").exists()
        )
        self.assertTrue(
            HistoricalEditableTextBlock.objects.filter(
                slug="keep_me"
            ).exists()
        )