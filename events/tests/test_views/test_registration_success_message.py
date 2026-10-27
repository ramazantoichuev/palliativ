from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from common.tests.tests_mixins import RateLimitCacheResetMixin
from events.models import EventRegistration
from events.tests.factories import EventFactory, PastEventFactory

SUCCESS_MESSAGES = {
    "ru": "Вы успешно зарегистрированы на мероприятие!",
    "ky": "Сиз иш-чарага ийгиликтүү катталдыңыз!",
    "en": "You have successfully registered for the event!",
}


class RegistrationSuccessMessageTests(RateLimitCacheResetMixin, TestCase):
    """После регистрации на мероприятие посетитель видит сообщение об успехе (Ticket 125)."""

    @classmethod
    def setUpTestData(cls):
        cls.event = EventFactory(slug="success-message", image=None)
        cls.url = reverse("events:event_detail", args=[cls.event.slug])
        cls.valid_data = {
            "full_name": "Иванов Иван Иванович",
            "email": "ivan@example.com",
            "phone": "+996700123456",
            "cf-turnstile-response": "dummy_token",
        }

    def setUp(self):
        super().setUp()
        patcher = patch(
            "common.turnstile_form.verify_turnstile_token", return_value=True
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        # LocaleMiddleware активирует язык на поток и не сбрасывает его —
        # возвращаем русский, чтобы не портить соседние тесты.
        self.addCleanup(translation.activate, "ru")

    def test_valid_registration_shows_success_message(self):
        response = self.client.post(self.url, data=self.valid_data, follow=True)

        self.assertContains(response, SUCCESS_MESSAGES["ru"])
        self.assertEqual(EventRegistration.objects.count(), 1)

    def test_invalid_form_shows_no_success_message(self):
        for missing_field in ("full_name", "phone"):
            with self.subTest(missing_field=missing_field):
                data = {**self.valid_data, missing_field: ""}

                response = self.client.post(self.url, data=data, follow=True)

                self.assertNotContains(response, SUCCESS_MESSAGES["ru"])
                self.assertFalse(EventRegistration.objects.exists())

    def test_past_event_shows_no_success_message(self):
        past_event = PastEventFactory(slug="past-success-message")
        past_url = reverse("events:event_detail", args=[past_event.slug])

        response = self.client.post(past_url, data=self.valid_data, follow=True)

        self.assertNotContains(response, SUCCESS_MESSAGES["ru"])
        self.assertFalse(EventRegistration.objects.exists())

    def test_filled_honeypot_shows_same_success_message_without_registration(self):
        data = {**self.valid_data, "company_site": "http://spam.example"}

        response = self.client.post(self.url, data=data, follow=True)

        self.assertContains(response, SUCCESS_MESSAGES["ru"])
        self.assertFalse(EventRegistration.objects.exists())

    def test_success_message_is_translated_on_ky_and_en(self):
        for i, lang in enumerate(("ky", "en")):
            with self.subTest(lang=lang):
                self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = lang
                # разные телефоны, чтобы не зависеть от защиты от дублей
                data = {**self.valid_data, "phone": f"+99670012346{i}"}

                response = self.client.post(self.url, data=data, follow=True)

                self.assertContains(response, SUCCESS_MESSAGES[lang])
                self.assertNotContains(response, SUCCESS_MESSAGES["ru"])
