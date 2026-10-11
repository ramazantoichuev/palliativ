from django.db import migrations

def remove_hey(apps, schema_editor):
    EditableTextBlock = apps.get_model("main", "EditableTextBlock")
    HistoricalEditableTextBlock = apps.get_model("main", "HistoricalEditableTextBlock")

    EditableTextBlock.objects.filter(slug="hey").delete()
    HistoricalEditableTextBlock.objects.filter(slug="hey").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_editabletextblock_slug_and_more'),
    ]

    operations = [
        migrations.RunPython(remove_hey, migrations.RunPython.noop),
    ]

