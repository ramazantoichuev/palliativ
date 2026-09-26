from unittest.mock import patch

from django.test import TestCase

from common.tests.tests_mixins import FormTurnstileIntegrationMixin
from events.forms import EventRegistrationForm


def build_form_data():
    return {
        "full_name": "Иванов Иван Иванович",
        "email": "ivanov@example.com",
        "phone": "+996700123456",
        "cf-turnstile-response": "dummy_token",
    }


@patch("common.turnstile_form.verify_turnstile_token", return_value=True)
class EventRegistrationFormValidationTests(TestCase):
    def test_valid_data_is_accepted(self, mock_verify):
        form = EventRegistrationForm(data=build_form_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_full_name_is_invalid(self, mock_verify):
        data = build_form_data()
        data["full_name"] = ""
        form = EventRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_invalid_email_is_invalid(self, mock_verify):
        data = build_form_data()
        data["email"] = "not-an-email"
        form = EventRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_phone_is_invalid(self, mock_verify):
        data = build_form_data()
        data["phone"] = ""
        form = EventRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)


class EventRegistrationFormTurnstileTests(FormTurnstileIntegrationMixin, TestCase):
    form_class = EventRegistrationForm
    base_form_data = {
        "full_name": "Иванов Иван Иванович",
        "email": "ivanov@example.com",
        "phone": "+996700123456",
    }
    turnstile_patch_path = "common.turnstile_form.verify_turnstile_token"