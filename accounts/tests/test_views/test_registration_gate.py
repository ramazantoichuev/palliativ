from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from main.models.system_settings import SystemSettings

User = get_user_model()


class PatientRegisterViewGateTests(TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("accounts:patient_register")
        self.turnstile_patcher = patch(
            "common.turnstile_form.verify_turnstile_token", return_value=True
        )
        self.turnstile_patcher.start()

    def tearDown(self):
        self.turnstile_patcher.stop()
        super().tearDown()

    def valid_data(self):
        return {
            "first_name": "Айгуль",
            "last_name": "Токтосунова",
            "email": "gate_patient@test.kg",
            "phone": "+996700900001",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "cf-turnstile-response": "dummy_token",
        }

    def test_get_shows_form_when_registration_enabled(self):
        SystemSettings.objects.create(patient_registration_enabled=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/patient_register.html")

    def test_get_shows_disabled_message_when_registration_disabled(self):
        SystemSettings.objects.create(patient_registration_enabled=False)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/registration_disabled.html")
        self.assertNotContains(response, 'name="email"')

    def test_post_creates_user_when_registration_enabled(self):
        SystemSettings.objects.create(patient_registration_enabled=True)

        self.client.post(self.url, data=self.valid_data())

        self.assertTrue(User.objects.filter(email="gate_patient@test.kg").exists())

    def test_post_does_not_create_user_when_registration_disabled(self):
        SystemSettings.objects.create(patient_registration_enabled=False)

        response = self.client.post(self.url, data=self.valid_data())

        self.assertFalse(User.objects.filter(email="gate_patient@test.kg").exists())
        self.assertTemplateUsed(response, "accounts/registration_disabled.html")


class DoctorRegisterViewGateTests(TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("accounts:doctor_register")
        self.turnstile_patcher = patch(
            "common.turnstile_form.verify_turnstile_token", return_value=True
        )
        self.turnstile_patcher.start()

    def tearDown(self):
        self.turnstile_patcher.stop()
        super().tearDown()

    def valid_data(self):
        return {
            "first_name": "Марат",
            "last_name": "Абдыкадыров",
            "email": "gate_doctor@test.kg",
            "phone": "+996700900002",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "education": "КГМА, лечебное дело",
            "skills": "Паллиативная помощь",
            "cf-turnstile-response": "dummy_token",
        }

    def test_get_shows_form_when_registration_enabled(self):
        SystemSettings.objects.create(doctor_registration_enabled=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/doctor_register.html")

    def test_get_shows_disabled_message_when_registration_disabled(self):
        SystemSettings.objects.create(doctor_registration_enabled=False)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/registration_disabled.html")

    def test_post_creates_user_when_registration_enabled(self):
        SystemSettings.objects.create(doctor_registration_enabled=True)

        self.client.post(self.url, data=self.valid_data())

        self.assertTrue(User.objects.filter(email="gate_doctor@test.kg").exists())

    def test_post_does_not_create_user_when_registration_disabled(self):
        SystemSettings.objects.create(doctor_registration_enabled=False)

        response = self.client.post(self.url, data=self.valid_data())

        self.assertFalse(User.objects.filter(email="gate_doctor@test.kg").exists())
        self.assertTemplateUsed(response, "accounts/registration_disabled.html")