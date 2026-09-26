from unittest.mock import patch

from django.test import TestCase

from accounts.forms import PatientRegistrationForm
from accounts.tests.factories import User
from common.tests.tests_mixins import FormTurnstileIntegrationMixin


@patch("common.turnstile_form.verify_turnstile_token", return_value=True)
class PatientRegistrationFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "first_name": "Айгуль",
            "last_name": "Токтосунова",
            "email": "aigul@test.kg",
            "phone": "+996700000050",
            "password1": "strongpass1",
            "password2": "strongpass1",
            "cf-turnstile-response": "dummy_token",
        }
        data.update(overrides)
        return data

    def test_valid_data_creates_patient(self, mock_verify):
        form = PatientRegistrationForm(self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertTrue(user.is_approved)

    def test_password_mismatch_is_invalid(self, mock_verify):
        form = PatientRegistrationForm(self._valid_data(password2="different"))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_duplicate_phone_is_invalid(self, mock_verify):
        PatientRegistrationForm(self._valid_data()).save()
        form = PatientRegistrationForm(self._valid_data(email="another@test.kg"))

        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)


class PatientRegistrationFormTurnstileTests(FormTurnstileIntegrationMixin, TestCase):
    form_class = PatientRegistrationForm
    base_form_data = {
        "first_name": "Айгуль",
        "last_name": "Токтосунова",
        "email": "aigul2@test.kg",
        "phone": "+996700000051",
        "password1": "strongpass1",
        "password2": "strongpass1",
    }
    turnstile_patch_path = "common.turnstile_form.verify_turnstile_token"