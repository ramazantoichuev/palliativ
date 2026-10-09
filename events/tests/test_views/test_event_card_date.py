from django.test import TestCase
from django.urls import reverse

from events.tests.factories import EventFactory, PastEventFactory, make_image


class EventCardDateTests(TestCase):

    def test_event_without_image_shows_date_overlay_on_placeholder(self):
        EventFactory(image=None)

        response = self.client.get(reverse("events:event_list"))

        self.assertContains(response, "event-date-overlay")
        self.assertContains(response, "event-placeholder.jpg")
        self.assertNotContains(response, "event-date-badge")

    def test_event_with_image_shows_corner_badge(self):
        EventFactory(image=make_image())

        response = self.client.get(reverse("events:event_list"))

        self.assertContains(response, "event-date-badge")
        self.assertNotContains(response, "event-date-overlay")

    def test_past_event_without_image_shows_date_overlay(self):
        PastEventFactory(image=None)

        response = self.client.get(reverse("events:event_list"))

        self.assertContains(response, "event-date-overlay")

    def test_home_page_event_card_shows_date_overlay(self):
        EventFactory(image=None)

        response = self.client.get(reverse("main:home"))

        self.assertContains(response, "event-date-overlay")