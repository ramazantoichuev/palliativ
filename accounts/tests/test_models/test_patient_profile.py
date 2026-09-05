from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import PatientProfile
from accounts.tests.factories import UserFactory

User = get_user_model()

class PatientProfileModelTest(TestCase):

    def test_related_name_patient_profile(self):
        user = UserFactory(role=User.Role.PATIENT)
        self.assertTrue(hasattr(user, 'patient_profile'))
        self.assertIsInstance(user.patient_profile, PatientProfile)

    def test_non_patient_role_has_no_patient_profile(self):
        user = UserFactory(role=User.Role.DOCTOR)
        self.assertFalse(hasattr(user, "patient_profile"))

    def test_patient_profile_deleted_when_user_deleted(self):
        user = UserFactory(role=User.Role.PATIENT)
        profile_id = user.patient_profile.id
        user.delete()

        self.assertFalse(PatientProfile.objects.filter(id=profile_id).exists())

