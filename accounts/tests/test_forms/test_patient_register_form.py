from django.test import TestCase

from accounts.forms import PatientRegistrationForm
from accounts.tests.factories import User


class PatientRegistrationFormTests(TestCase):

    def _valid_data(self, **overrides):
        data = {
            "first_name": "Айгуль",
            "last_name": "Токтосунова",
            "email": "aigul@test.kg",
            "phone": "+996700000050",
            "password1": "strongpass1",
            "password2": "strongpass1",
        }
        data.update(overrides)
        return data

    def test_valid_data_creates_patient(self):
        form = PatientRegistrationForm(self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertTrue(user.is_approved)

    def test_password_mismatch_is_valid(self):
        form = PatientRegistrationForm(self._valid_data(password2='different'))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
