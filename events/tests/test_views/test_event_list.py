from django.test import TestCase
from django.urls import reverse

from events.models import Event


class EventListViewTest(TestCase):
    def setUp(self):
        self.event1 = Event.objects.create(
            title='wertyuk1',
            description='test1',
            content='test1',
            event_date='2026-08-22 00:00:00',
            location='test1'
        )
        self.event2 = Event.objects.create(
            title='wertyuk',
            description='test',
            content='test',
            event_date='2026-08-28 00:00:00',
            location='test'
        )

    def  test_event_list_separation(self):
        url = reverse('events:event_list')
        response = self.client.get(url)

        self.assertTrue(self.event1 in response.context['past_events'])
        self.assertTrue(self.event2 in response.context['upcoming_events'])