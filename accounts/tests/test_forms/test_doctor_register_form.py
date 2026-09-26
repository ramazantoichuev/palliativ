from unittest.mock import patch

from django.test import TestCase

from accounts.forms import DoctorApplicationForm
from accounts.tests.factories import User
from common.tests.tests_mixins import FormTurnstileIntegrationMixin


@patch("common.turnstile_form.verify_turnstile_token", return_value=True)
class DoctorApplicationFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "first_name": "Марат",
            "last_name": "Иманалиев",
            "email": "marat@test.kg",
            "phone": "+996700000060",
            "password1": "strongpass1",
            "password2": "strongpass1",
            "education": "КГМА, лечебное дело",
            "skills": "Паллиативная помощь, обезболивание",
            "cf-turnstile-response": "dummy_token",
        }
        data.update(overrides)
        return data

    def test_valid_data_creates_doctor_not_approved(self, mock_verify):
        form = DoctorApplicationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertEqual(user.role, User.Role.DOCTOR)
        self.assertFalse(user.is_approved)
        self.assertEqual(user.doctor_profile.education, "КГМА, лечебное дело")

    def test_password_mismatch_is_invalid(self, mock_verify):
        form = DoctorApplicationForm(data=self._valid_data(password2="different"))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

class DoctorApplicationFormTurnstileTests(FormTurnstileIntegrationMixin, TestCase):
    form_class = DoctorApplicationForm
    base_form_data = {
        "first_name": "Марат",
        "last_name": "Иманалиев",
        "email": "marat2@test.kg",
        "phone": "+996700000061",
        "password1": "strongpass1",
        "password2": "strongpass1",
        "education": "КГМА, лечебное дело",
        "skills": "Паллиативная помощь",
    }
    turnstile_patch_path = "common.turnstile_form.verify_turnstile_token"