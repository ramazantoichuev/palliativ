from django.db import migrations


def copy_name_to_name_ru(apps, schema_editor):
    Symptom = apps.get_model('patients', 'Symptom')
    for symptom in Symptom.objects.filter(name_ru__isnull=True):
        symptom.name_ru = symptom.name
        symptom.save(update_fields=['name_ru'])


def reverse_copy(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_symptom_name_en_symptom_name_ky_symptom_name_ru'),
    ]

    operations = [
        migrations.RunPython(copy_name_to_name_ru, reverse_copy),
    ]
