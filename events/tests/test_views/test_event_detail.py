from datetime import date

from django.test import TestCase
from django.urls import reverse

from events.models import Event, EventRegistration  # поправьте путь импорта


class EventRegistrationSuccessTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='wertyuk1',
            description='test1',
            content='test1',
            event_date='2026-08-22 00:00:00',
            location='test1'
        )
        self.url = reverse('events:event_detail', kwargs={'slug': self.event.slug})

    def test_successful_registration_creates_event_registration(self):
        data = {
            'full_name': 'Иванов Иван Иванович',
            'email': 'ivanov@example.com',
            'phone': '+996700123456',
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventRegistration.objects.count(), 1)
        registration = EventRegistration.objects.first()
        self.assertEqual(registration.event, self.event)
        self.assertEqual(registration.full_name, data['full_name'])
        self.assertEqual(registration.email, data['email'])
        self.assertEqual(registration.phone, data['phone'])

    def test_successful_registration_redirects(self):
        data = {
            'full_name': 'Иванов Иван Иванович',
            'email': 'ivanov@example.com',
            'phone': '+996700123456',
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.url)