from django.test import TestCase

from accounts.forms import DoctorApplicationForm
from accounts.tests.factories import User


class PatientRegistrationFormTests(TestCase):

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
        }
        data.update(overrides)
        return data

    def test_valid_data_creates_doctor_not_approved(self):
        form = DoctorApplicationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertEqual(user.role, User.Role.DOCTOR)
        self.assertFalse(user.is_approved)
        self.assertEqual(user.doctor_profile.education, "КГМА, лечебное дело")

    def test_password_mismatch_is_invalid(self):
        form = DoctorApplicationForm(data=self._valid_data(password2="different"))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

