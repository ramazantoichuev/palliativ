import tempfile

from django.test import TestCase, override_settings
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

    def test_clinics_card_removed(self):
        response = self.client.get(self.url)

        self.assertNotContains(response, "Для клиник")

    def test_patients_card_has_three_clickable_links(self):
        response = self.client.get(self.url)
        self.assertContains(
            response, 'href="/resources/?audience=caregiver"'
        )
        self.assertContains(
            response,
            'href="/resources/?audience=caregiver&subcategory=pain_management"',
        )
        self.assertContains(
            response,
            'href="/resources/?audience=caregiver&subcategory=meds_rights"',
        )

    def test_doctors_card_is_fully_clickable(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'href="/resources/?audience=specialist"')

    def test_text_blocks_render_from_fallback_when_no_db_record(self):
        from main.models.editable_text_block import EditableTextBlock
        EditableTextBlock.objects.filter(slug="home_hero_title").delete()
        response = self.client.get(self.url)
        self.assertContains(response, "Жизнь без боли")

    def test_text_blocks_render_from_db_when_present(self):
        from main.models.editable_text_block import EditableTextBlock
        EditableTextBlock.objects.update_or_create(
            slug="home_hero_title", defaults={"content": "Кастомный заголовок"}
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Кастомный заголовок")
        
    def test_post_without_image_renders_placeholder_on_home(self):
        with (
            tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as media_root,
            override_settings(MEDIA_ROOT=media_root),
        ):
            PostFactory(image=None)
            response = self.client.get(self.url)
            self.assertContains(response, "main/images/news-placeholder.jpg")

    def test_event_without_image_renders_placeholder_on_home(self):
        EventFactory()
        response = self.client.get(self.url)
        self.assertContains(response, "main/images/event-placeholder.jpg")
