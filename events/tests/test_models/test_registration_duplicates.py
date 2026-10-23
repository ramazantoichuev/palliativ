from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from events.models import EventRegistration
from events.tests.factories import EventFactory


class EventRegistrationSpamTests(TestCase):
    def setUp(self):
        cache.clear()
        self.event = EventFactory(image=None)
        self.url = reverse("events:event_detail", kwargs={"slug": self.event.slug})
        for target in ("events.views.notify_admins", "events.views.send_confirmation"):
            patcher = mock.patch(target)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _post(self, phone="0555123456", event=None, **extra):
        url = self.url
        if event:
            url = reverse("events:event_detail", kwargs={"slug": event.slug})
        data = {"full_name": "Айгуль", "email": "", "phone": phone}
        data.update(extra)
        return self.client.post(url, data)

    def test_same_phone_on_same_event_is_rejected(self):
        self._post()
        response = self._post()

        self.assertContains(response, "Вы уже зарегистрированы на это мероприятие")
        self.assertEqual(EventRegistration.objects.count(), 1)

    def test_same_phone_in_other_format_is_rejected(self):
        self._post(phone="0555123456")
        response = self._post(phone="+996 555 123 456")

        self.assertContains(response, "Вы уже зарегистрированы на это мероприятие")
        self.assertEqual(EventRegistration.objects.count(), 1)

    def test_same_phone_on_other_event_is_allowed(self):
        other = EventFactory(image=None)
        self._post()
        self._post(event=other)

        self.assertEqual(EventRegistration.objects.count(), 2)

    def test_filled_honeypot_creates_nothing(self):
        response = self._post(company_site="http://spam.example")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventRegistration.objects.count(), 0)