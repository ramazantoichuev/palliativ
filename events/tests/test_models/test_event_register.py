from django.test import TestCase

from events.models import Event, EventRegistration


class EventRegistrationModelTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='testing',
            description='test',
            content='test',
            event_date='2026-08-24 00:00:00',
            location='test')

    def test_create_registration(self):
        registration = EventRegistration.objects.create(
            event=self.event,
            full_name="Иванов Иван Иванович",
            email="ivanov@example.com",
            phone="+996700123456",
        )

        self.assertEqual(registration.event, self.event)
        self.assertEqual(registration.full_name, "Иванов Иван Иванович")
        self.assertEqual(registration.email, "ivanov@example.com")
        self.assertEqual(registration.phone, "+996700123456")

    def test_status_defaults_to_false(self):
        registration = EventRegistration.objects.create(
            event=self.event,
            full_name="Иванов Иван",
            email="ivanov@example.com",
            phone="+996700123456",
        )

        self.assertFalse(registration.status)

    def test_str_representation(self):
        registration = EventRegistration.objects.create(
            event=self.event,
            full_name="Иванов Иван",
            email="ivanov@example.com",
            phone="+996700123456",
        )

        self.assertEqual(str(registration), f"Иванов Иван — {self.event.title}")