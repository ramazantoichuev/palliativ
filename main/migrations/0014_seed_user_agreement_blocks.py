from django.db import migrations

SLUGS = (
    "user-agreement-intro",
    "user-agreement-general",
    "user-agreement-nature",
    "user-agreement-duties",
    "user-agreement-ip",
    "user-agreement-liability",
    "user-agreement-changes",
    "user-agreement-law",
)


def seed_blocks(apps, schema_editor):
    """Создаёт пустые блоки соглашения, чтобы менеджер заполнял их, а не вводил slug руками.

    Пока хотя бы один блок пуст, страница соглашения скрыта (main/user_agreement.py).
    """
    EditableTextBlock = apps.get_model("main", "EditableTextBlock")
    for slug in SLUGS:
        EditableTextBlock.objects.get_or_create(
            slug=slug, defaults={"content": "", "content_ru": ""}
        )


def remove_empty_blocks(apps, schema_editor):
    """Откат удаляет только пустые блоки, чтобы не стереть внесённый текст."""
    EditableTextBlock = apps.get_model("main", "EditableTextBlock")
    for block in EditableTextBlock.objects.filter(slug__in=SLUGS):
        if not (block.content_ru or block.content or "").strip():
            block.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0013_remove_test_block_hey"),
    ]

    operations = [
        migrations.RunPython(seed_blocks, remove_empty_blocks),
    ]
