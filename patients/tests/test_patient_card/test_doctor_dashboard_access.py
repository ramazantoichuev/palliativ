from django.test import TestCase
from django.urls import reverse

from accounts.models import BaseUser


class DoctorDashboardAccessTests(TestCase):
    def setUp(self):
        self.url = reverse("patients:doctor_dashboard")

    def _create_user(self, role, number):
        return BaseUser.objects.create_user(
            username=f"user_{role}",
            password="password123",
            email=f"user_{role}@example.com",
            phone=f"+99655500{number:04d}",
            role=role,
        )

    def test_anonymous_user_is_redirected_to_login_with_next(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn(f"next={self.url}", response.url)

    def test_non_doctor_roles_get_403(self):
        roles = [
            BaseUser.Role.PATIENT,
            BaseUser.Role.MANAGER,
            BaseUser.Role.MODERATOR,
            BaseUser.Role.ADMIN,
        ]
        for number, role in enumerate(roles, start=1):
            with self.subTest(role=role):
                user = self._create_user(role, number)
                self.client.force_login(user)

                response = self.client.get(self.url)

                self.assertEqual(response.status_code, 403)

    def test_doctor_gets_200(self):
        doctor = self._create_user(BaseUser.Role.DOCTOR, 10)
        self.client.force_login(doctor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)