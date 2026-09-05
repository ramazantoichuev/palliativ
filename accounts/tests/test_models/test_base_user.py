from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import DoctorProfile, PatientProfile
from accounts.tests.factories import UserFactory

User = get_user_model()

class BaseUserTest(TestCase):

    def test_patient_is_approved_automatically(self):
        user = UserFactory(role=User.Role.PATIENT)
        self.assertTrue(user.is_approved)

    def test_doctor_is_not_approved_automatically(self):
        user = UserFactory(role=User.Role.DOCTOR)
        self.assertFalse(user.is_approved)

    def test_admin_is_approved_and_staff_and_superuser(self):
        user = UserFactory(role=User.Role.ADMIN)
        self.assertTrue(user.is_approved)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_manager_is_staff_but_not_superuser(self):
        user = UserFactory(role=User.Role.MANAGER)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_default_role_is_patient(self):
        user = UserFactory()
        self.assertEqual(user.role, User.Role.PATIENT)

    def test_doctor_profile_created_automatically(self):
        user = UserFactory(role=User.Role.DOCTOR)
        self.assertTrue(DoctorProfile.objects.filter(user=user).exists())

    def test_patient_profile_created_automatically(self):
        user = UserFactory(role=User.Role.PATIENT)
        self.assertTrue(PatientProfile.objects.filter(user=user).exists())

    def test_admin_has_no_doctor_or_patient_profile(self):
        user = UserFactory(role=User.Role.ADMIN)
        self.assertFalse(DoctorProfile.objects.filter(user=user).exists())
        self.assertFalse(PatientProfile.objects.filter(user=user).exists())

    def test_duplicate_email_not_allowed(self):
        UserFactory(email="dup@mail.ru")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="another",
                    email="dup@mail.ru",
                    password="somepass123",
                    first_name="Т",
                    last_name="Т",
                    phone="+996700000098",
                )

    def test_duplicate_phone_not_allowed(self):
        UserFactory(phone="+996700000099")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="another2",
                    email="another2@mail.ru",
                    password="somepass123",
                    first_name="Т",
                    last_name="Т",
                    phone="+996700000099",
                )

class BaseUserGroupAssignmentTest(TestCase):

    def test_manager_saved_without_group_does_not_fail_and_logs_warning(self):
        with self.assertLogs('accounts.models', level='WARNING') as log_context:
            user = UserFactory(role=User.Role.MANAGER)

        self.assertTrue(user.pk)
        self.assertEqual(user.groups.count(), 0)
        self.assertIn('Managers', log_context.output[0])

    def test_moderator_saved_without_group_does_not_fail_and_logs_warning(self):

        with self.assertLogs('accounts.models', level='WARNING') as log_context:
            user = UserFactory(role=User.Role.MODERATOR)

        self.assertTrue(user.pk)
        self.assertEqual(user.groups.count(), 0)
        self.assertIn('Moderators', log_context.output[0])

    def test_manager_saved_with_existing_group_is_added_to_it(self):
        from django.contrib.auth.models import Group
        Group.objects.create(name='Managers')

        user = UserFactory(role=User.Role.MANAGER)

        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(user.groups.first().name, 'Managers')

    def test_patient_role_has_no_group_and_no_log(self):
        user = UserFactory(role=User.Role.PATIENT)

        self.assertEqual(user.groups.count(), 0)