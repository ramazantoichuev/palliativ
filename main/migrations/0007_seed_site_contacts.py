from django.db import migrations


def seed_site_contacts(apps, schema_editor):
    SiteContacts = apps.get_model("main", "SiteContacts")
    if SiteContacts.objects.exists():
        return
    SiteContacts.objects.create(
        pk=1,
        phone="+996312214015",
        phone_display="0312 214015",
        email="info@palliativ.kg",
        whatsapp_url="https://wa.me/996555922604",
        whatsapp_display="+996 555 922 604",
        facebook_url="https://www.facebook.com/palliativecare.kg",
        instagram_url="https://www.instagram.com/palliativecare_kg",
        twogis_url="https://2gis.kg/bishkek/geo/70000001117702816",
        address="г. Бишкек, ул. Юдахина 61",
        address_ru="г. Бишкек, ул. Юдахина 61",
        address_en="Bishkek, 61 Yudakhin St.",
        address_ky="Бишкек ш., Юдахин көч. 61",
    )


def unseed_site_contacts(apps, schema_editor):
    apps.get_model("main", "SiteContacts").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_sitecontacts"),
    ]

    operations = [
        migrations.RunPython(seed_site_contacts, unseed_site_contacts),
    ]
