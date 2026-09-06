from django.test import TestCase
from django.utils.text import slugify

from events.models import Event


class TestEvent(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='wertyuk',
            description='test',
            content='test',
            event_date='2026-08-24 00:00:00',
            location='test'
        )

    def test_event_creation(self):


        self.assertIn(self.event, Event.objects.all())

    def test_event_slug(self):
        self.assertEqual(slugify(self.event.title, allow_unicode=True), self.event.slug)




