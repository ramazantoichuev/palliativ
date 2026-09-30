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

    def test_participation_link_stays_in_navigation_when_both_disabled(self):
        SystemSettings.objects.create(
            patient_registration_enabled=False,
            doctor_registration_enabled=False,
        )

        response = self.client.get(self.url)

        self.assertContains(response, self.url)