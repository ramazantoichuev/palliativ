from django.test import TestCase
from django.urls import reverse

from events.tests.factories import EventFactory, PastEventFactory
from news.tests.factories import PostFactory


class HomeViewTest(TestCase):

    def setUp(self):
        self.url = reverse("main:home")

    def test_home_page_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_shows_exactly_3_latest_posts(self):
        posts = [PostFactory() for _ in range(5)]
        response = self.client.get(self.url)
        latest_posts = response.context["latest_posts"]

        self.assertEqual(len(latest_posts), 3)
        expected_order = list(reversed(posts))[:3]
        self.assertEqual(list(latest_posts), expected_order)

    def test_shows_exactly_3_upcoming_events_excludes_past(self):
        upcoming = [EventFactory() for _ in range(4)]
        past = PastEventFactory()

        response = self.client.get(self.url)
        upcoming_events = response.context["upcoming_events"]

        self.assertEqual(len(upcoming_events), 3)
        self.assertNotIn(past, upcoming_events)
        for event in upcoming_events:
            self.assertIn(event, upcoming)

    def test_empty_state_no_posts_no_events(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["latest_posts"]), 0)
        self.assertEqual(len(response.context["upcoming_events"]), 0)
        self.assertNotContains(response, "Все новости")
        self.assertNotContains(response, "Все мероприятия")
