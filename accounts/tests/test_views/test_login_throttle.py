from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.tests.tests_mixins import RateLimitCacheResetMixin

User = get_user_model()
PASSWORD = "StrongPass12345"
LIMIT = 10


class LoginThrottleTests(RateLimitCacheResetMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password=PASSWORD,
            role=User.Role.PATIENT,
        )

    def _login(self, password):
        return self.client.post(
            self.url, {"username": "user1@example.com", "password": password}
        )

    def test_eleventh_failed_attempt_is_blocked(self):
        for _ in range(LIMIT):
            self.assertEqual(self._login("wrong").status_code, 200)

        response = self._login("wrong")
        self.assertContains(response, "Слишком много попыток", status_code=429)

    def test_correct_password_is_also_blocked_after_limit(self):
        for _ in range(LIMIT):
            self._login("wrong")

        self.assertEqual(self._login(PASSWORD).status_code, 429)

    def test_successful_logins_do_not_count(self):
        for _ in range(LIMIT + 5):
            self.assertEqual(self._login(PASSWORD).status_code, 302)
            self.client.logout()

        self.assertEqual(self._login("wrong").status_code, 200)