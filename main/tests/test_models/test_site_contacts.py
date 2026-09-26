from django.test import TestCase
from django.urls import reverse

from main.models.site_contacts import SiteContacts


class TestSiteContactsSingleton(TestCase):

    def test_seed_migration_created_single_record_with_real_values(self):
        contacts = SiteContacts.load()

        self.assertEqual(SiteContacts.objects.count(), 1)
        self.assertEqual(contacts.phone, "+996312214015")
        self.assertEqual(contacts.phone_display, "0312 214015")
        self.assertEqual(contacts.email, "info@palliativ.kg")

    def test_save_never_creates_second_record(self):
        another = SiteContacts(
            phone="+996312000000",
            phone_display="0312 000000",
            email="new@palliativ.kg",
            address="г. Бишкек",
        )

        another.save()

        self.assertEqual(SiteContacts.objects.count(), 1)
        self.assertEqual(SiteContacts.load().email, "new@palliativ.kg")

    def test_url_handles_are_derived_from_urls(self):
        contacts = SiteContacts.load()

        self.assertEqual(contacts.instagram_handle, "palliativecare_kg")
        self.assertEqual(contacts.facebook_handle, "palliativecare.kg")


class TestSiteContactsRendering(TestCase):

    def test_footer_renders_values_from_model_on_any_page(self):
        contacts = SiteContacts.load()
        contacts.phone = "+996312999999"
        contacts.phone_display = "0312 999999"
        contacts.email = "changed@palliativ.kg"
        contacts.save()

        response = self.client.get(reverse("main:home"))

        self.assertContains(response, 'tel:+996312999999')
        self.assertContains(response, "0312 999999")
        self.assertContains(response, "changed@palliativ.kg")

    def test_contacts_page_renders_values_from_model(self):
        response = self.client.get(reverse("main:contacts"))

        self.assertContains(response, 'tel:+996312214015')
        self.assertContains(response, "0312 214015")
        self.assertContains(response, "info@palliativ.kg")
        self.assertContains(response, "https://wa.me/996555922604")
        self.assertContains(response, "+996 555 922 604")
        self.assertContains(response, "palliativecare_kg")

    def test_empty_social_url_hides_footer_icon(self):
        contacts = SiteContacts.load()
        contacts.facebook_url = ""
        contacts.instagram_url = ""
        contacts.save()

        response = self.client.get(reverse("main:home"))

        self.assertNotContains(response, "fa-facebook")
        self.assertNotContains(response, "fa-instagram")
        self.assertContains(response, "fa-whatsapp")
