
from django.test import TestCase
from django.urls import reverse

from events.models import Event


class ContentLanguageTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='test',
            description='test1',
            content='тест',
            content_ky="Кыргызча контент",
            content_en="English content",
            event_date='2026-08-22 00:00:00',
            location='test1'
        )


    def test_content_ky(self):
        self.client.cookies["django_language"] = "ky"
        response = self.client.get(reverse("events:event_detail", kwargs={'slug': self.event.slug}))

        self.assertEqual(response.context_data['event'].content, 'Кыргызча контент')


    def test_content_en(self):
        self.client.cookies["django_language"] = "en"
        response = self.client.get(reverse("events:event_detail", kwargs={'slug': self.event.slug}))

        self.assertEqual(response.context_data['event'].content, 'English content')