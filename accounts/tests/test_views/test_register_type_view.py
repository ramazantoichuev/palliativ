from django.test import TestCase
from django.urls import reverse

from main.models.system_settings import SystemSettings


class RegisterTypeViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("accounts:register_type")

    def test_both_enabled_shows_both_buttons(self):
        SystemSettings.objects.create(
            patient_registration_enabled=True,
            doctor_registration_enabled=True,
        )

        response = self.client.get(self.url)

        self.assertContains(response, reverse("accounts:patient_register"))
        self.assertContains(response, reverse("accounts:doctor_register"))
        self.assertNotContains(response, "Регистрация временно недоступна, попробуйте позже.")

    def test_only_patient_disabled_shows_doctor_button_and_patient_message(self):
        SystemSettings.objects.create(
            patient_registration_enabled=False,
            doctor_registration_enabled=True,
        )

        response = self.client.get(self.url)

        self.assertNotContains(response, reverse("accounts:patient_register"))
        self.assertContains(response, reverse("accounts:doctor_register"))
        self.assertContains(response, "Регистрация временно недоступна")

    def test_only_doctor_disabled_shows_patient_button_and_doctor_message(self):
        SystemSettings.objects.create(
            patient_registration_enabled=True,
            doctor_registration_enabled=False,
        )

        response = self.client.get(self.url)

        self.assertContains(response, reverse("accounts:patient_register"))
        self.assertNotContains(response, reverse("accounts:doctor_register"))
        self.assertContains(response, "Регистрация временно недоступна")

    def test_both_disabled_shows_single_message_without_buttons(self):
        SystemSettings.objects.create(
            patient_registration_enabled=False,
            doctor_registration_enabled=False,
        )

        response = self.client.get(self.url)

        self.assertContains(response, "Регистрация временно недоступна, попробуйте позже.")
        self.assertNotContains(response, reverse("accounts:patient_register"))
        self.assertNotContains(response, reverse("accounts:doctor_register"))


class ParticipationNavItemTests(TestCase):
    """Пункт «Участие» в шапке скрыт, когда выключены обе регистрации (Ticket 110).

    Проверяем точный маркер ссылки меню href="...": в canonical/og:url адрес
    начинается с http://, поэтому совпадение возможно только для пункта меню.
    """

    nav_link_marker = 'href="/accounts/participation/"'

    def setUp(self):
        super().setUp()
        self.home_url = reverse("main:home")

    def test_link_shown_when_both_registrations_enabled(self):
        SystemSettings.objects.create(
            patient_registration_enabled=True,
            doctor_registration_enabled=True,
        )

        response = self.client.get(self.home_url)

        self.assertContains(response, self.nav_link_marker)

    def test_link_shown_when_only_patient_registration_enabled(self):
        SystemSettings.objects.create(
            patient_registration_enabled=True,
            doctor_registration_enabled=False,
        )

        response = self.client.get(self.home_url)

        self.assertContains(response, self.nav_link_marker)

    def test_link_shown_when_only_doctor_registration_enabled(self):
        SystemSettings.objects.create(
            patient_registration_enabled=False,
            doctor_registration_enabled=True,
        )

        response = self.client.get(self.home_url)

        self.assertContains(response, self.nav_link_marker)

    def test_link_hidden_when_both_registrations_disabled(self):
        SystemSettings.objects.create(
            patient_registration_enabled=False,
            doctor_registration_enabled=False,
        )

        response = self.client.get(self.home_url)

        self.assertNotContains(response, self.nav_link_marker)
        # остальные пункты меню на месте
        self.assertContains(response, 'href="/about/"')
        self.assertContains(response, 'href="/contacts/"')

    def test_direct_access_still_returns_200_when_both_disabled(self):
        SystemSettings.objects.create(
            patient_registration_enabled=False,
            doctor_registration_enabled=False,
        )

        response = self.client.get(reverse("accounts:register_type"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Регистрация временно недоступна, попробуйте позже."
        )