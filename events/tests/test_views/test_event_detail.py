import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from events.models import EventRegistration
from events.tests.factories import EventFactory, make_image


class TestEventDetailView(TestCase):
    """Детальная страница мероприятия: критерии приёмки 5-10."""

    @classmethod
    def setUpTestData(cls):
        cls.event = EventFactory(
            title='Школа паллиативной помощи',
            slug='school',
            description='Двухдневный семинар для медицинских работников.',
            content='В программе: лекции и разбор клинических случаев.',
            location='г. Бишкек, ул. Юдахина 61',
        )
        cls.url = reverse('events:event_detail', args=[cls.event.slug])
        cls.valid_data = {
            'full_name': 'Иванов Иван Иванович',
            'email': 'ivan@example.com',
            'phone': '+996700123456',
        }

    def test_page_opens_and_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_detail.html')

    def test_shows_title_date_time_and_location(self):
        response = self.client.get(self.url)
        expected_datetime = timezone.localtime(
            self.event.event_date).strftime('%d.%m.%Y %H:%M')

        self.assertContains(response, 'Школа паллиативной помощи')
        self.assertContains(response, expected_datetime)
        self.assertContains(response, 'г. Бишкек, ул. Юдахина 61')

    def test_shows_description_and_content(self):
        response = self.client.get(self.url)

        self.assertContains(response, 'Двухдневный семинар для медицинских работников.')
        self.assertContains(response, 'В программе: лекции и разбор клинических случаев.')

    def test_registration_form_is_available(self):
        response = self.client.get(self.url)

        self.assertIn('form', response.context)
        self.assertContains(response, 'name="full_name"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="phone"')

    def test_event_without_image_renders_without_img_tag(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<img')

    def test_event_image_is_rendered_when_present(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as media_root, \
                override_settings(MEDIA_ROOT=media_root):
            event = EventFactory(slug='with-image', image=make_image())

            response = self.client.get(
                reverse('events:event_detail', args=[event.slug]))

            self.assertContains(response, event.image.url)

    def test_valid_post_creates_registration_for_this_event(self):
        response = self.client.post(self.url, data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        registration = EventRegistration.objects.get()
        self.assertEqual(registration.event, self.event)
        self.assertEqual(registration.full_name, 'Иванов Иван Иванович')
        self.assertEqual(registration.email, 'ivan@example.com')
        self.assertEqual(registration.phone, '+996700123456')

    def test_valid_post_redirects_back_to_event_page(self):
        response = self.client.post(self.url, data=self.valid_data)

        self.assertRedirects(response, self.url)

    def test_invalid_post_does_not_create_registration(self):
        response = self.client.post(
            self.url,
            data={'full_name': '', 'email': 'not-an-email', 'phone': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(EventRegistration.objects.exists())
