from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from common.tests.tests_mixins import RateLimitCacheResetMixin
from main.models.consultation import ConsultationRequest

TOPICS = [c[0] for c in ConsultationRequest._meta.get_field("topic").choices]


class ConsultationSpamTests(RateLimitCacheResetMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.turnstile_patcher = patch(
            "common.turnstile_form.verify_turnstile_token",
            return_value=True,
        )
        self.turnstile_patcher.start()
        self.addCleanup(self.turnstile_patcher.stop)

        self.url = reverse("main:new-consultation")
        self.limit = settings.RATE_LIMITS["consultation"][0]

        for target in ("main.views.notify_admins", "main.views.send_confirmation"):
            patcher = mock.patch(target)
            mocked = patcher.start()
            self.addCleanup(patcher.stop)

            if target.endswith("notify_admins"):
                self.notify = mocked

    def _post(self, phone="0555123456", topic=None, **extra):
        data = {
            "first_name": "Айгуль",
            "phone": phone,
            "email": "a@example.com",
            "topic": topic or TOPICS[0],
        }
        return self.client.post(self.url, data, **extra)

    def test_request_over_limit_is_blocked(self):
        for i in range(self.limit):
            self._post(phone=f"055512345{i}")

        response = self._post(phone="0700123456")

        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "Слишком много попыток", status_code=429)
        self.assertEqual(ConsultationRequest.objects.count(), self.limit)
        self.assertEqual(self.notify.call_count, self.limit)

    def test_other_ip_is_not_blocked(self):
        for i in range(self.limit):
            self._post(phone=f"055512345{i}")

        response = self._post(
            phone="0700123456",
            HTTP_X_REAL_IP="8.8.8.8",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ConsultationRequest.objects.count(), self.limit + 1)

    def test_filled_honeypot_creates_nothing_and_shows_success(self):
        response = self.client.post(
            self.url,
            {
                "first_name": "Бот",
                "phone": "0555123456",
                "email": "b@example.com",
                "topic": TOPICS[0],
                "company_site": "http://spam.example",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ConsultationRequest.objects.count(), 0)
        self.notify.assert_not_called()

    def test_duplicate_within_window_creates_one_record(self):
        first = self._post()
        second = self._post()

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(ConsultationRequest.objects.count(), 1)
        self.assertEqual(self.notify.call_count, 1)

    def test_same_phone_other_topic_is_not_duplicate(self):
        if len(TOPICS) < 2:
            self.skipTest("нужны минимум две темы")

        self._post(topic=TOPICS[0])
        self._post(topic=TOPICS[1])

        self.assertEqual(ConsultationRequest.objects.count(), 2)
