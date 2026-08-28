import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from events.models import Event
from events.tests.factories import EventFactory, PastEventFactory, make_image


class TestEventListView(TestCase):
    """Страница списка мероприятий: критерии приёмки 1-5, 10, 11."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('events:event_list')
        cls.upcoming = EventFactory(
            title='Школа паллиативной помощи',
            slug='school',
            location='г. Бишкек, ул. Юдахина 61',
        )
        cls.past = PastEventFactory(title='Прошедшая конференция', slug='past-conf')

    def test_page_opens_and_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_list.html')

    def test_context_splits_events_into_upcoming_and_past(self):
        response = self.client.get(self.url)

        self.assertIn('upcoming_events', response.context)
        self.assertIn('past_events', response.context)
        self.assertIn(self.upcoming, response.context['upcoming_events'])
        self.assertNotIn(self.past, response.context['upcoming_events'])
        self.assertIn(self.past, response.context['past_events'])
        self.assertNotIn(self.upcoming, response.context['past_events'])

    def test_card_shows_title_date_time_and_location(self):
        response = self.client.get(self.url)
        expected_datetime = timezone.localtime(
            self.upcoming.event_date).strftime('%d.%m.%Y %H:%M')

        self.assertContains(response, 'Школа паллиативной помощи')
        self.assertContains(response, expected_datetime)
        self.assertContains(response, 'г. Бишкек, ул. Юдахина 61')

    def test_upcoming_and_past_events_both_link_to_detail_page(self):
        response = self.client.get(self.url)

        self.assertContains(
            response, reverse('events:event_detail', args=[self.upcoming.slug]))
        self.assertContains(
            response, reverse('events:event_detail', args=[self.past.slug]))

    def test_event_without_image_renders_without_img_tag(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<img')

    def test_event_image_is_rendered_when_present(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as media_root, \
                override_settings(MEDIA_ROOT=media_root):
            event = EventFactory(slug='with-image', image=make_image())

            response = self.client.get(self.url)

            self.assertContains(response, event.image.url)

    def test_empty_state_is_shown_when_no_upcoming_events(self):
        Event.objects.filter(pk=self.upcoming.pk).delete()

        response = self.client.get(self.url)

        self.assertContains(response, 'Пока нет предстоящих мероприятий')

    def test_interface_strings_go_through_translation(self):
        """Заголовки разделов не должны утекать в вёрстку по-русски при другом языке."""
        response = self.client.get(self.url, headers={'accept-language': 'en'})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Предстоящие мероприятия')
        self.assertNotContains(response, 'Прошедшие мероприятия')
