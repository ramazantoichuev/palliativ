from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import DoctorProfile
from accounts.tests.factories import UserFactory

User = get_user_model()


class DoctorProfileModelTest(TestCase):
    def test_default_fields_blank(self):
        user = UserFactory(role=User.Role.DOCTOR)
        self.assertEqual(user.doctor_profile.education, '')
        self.assertEqual(user.doctor_profile.skills, '')

    def test_one_to_one_unique(self):
        user = UserFactory(role=User.Role.DOCTOR)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DoctorProfile.objects.create(user=user)

    def test_deleted_on_user_delete(self):
        user = UserFactory(role=User.Role.DOCTOR)
        profile_id = user.doctor_profile.pk
        user.delete()

        self.assertFalse(DoctorProfile.objects.filter(id=profile_id).exists())

    def test_patient_has_no_doctor_profile(self):
        user = UserFactory(role=User.Role.PATIENT)
        self.assertFalse(hasattr(user, "doctor_profile"))

    def test_doctor_not_approved_by_default(self):
        user = UserFactory(role=User.Role.DOCTOR)
        self.assertFalse(user.is_approved)

