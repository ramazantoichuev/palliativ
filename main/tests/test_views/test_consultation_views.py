from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from main.models.consultation import ConsultationRequest


def build_valid_data():
    return {
        'first_name': 'Айгуль',
        'phone': '0555123456',
        'email': 'test@example.com',
        'topic': 'medical_help',
    }

@override_settings(NOTIFICATION_EMAILS=['admin@example.com'])
class TestConsultationCreateViewNotifications(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('main:new-consultation')
        cls.valid_data = {
            'first_name': 'Айгуль',
            'phone': '+996700123456',
            'email': 'client@example.com',
            'topic': 'medical_help',
        }

    def test_valid_submission_sends_admin_notification_and_confirmation(self):
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(len(mail.outbox), 2)
        recipients = [msg.to[0] for msg in mail.outbox]
        self.assertIn('admin@example.com', recipients)
        self.assertIn('client@example.com', recipients)

    def test_invalid_submission_sends_no_email(self):
        invalid_data = {**self.valid_data, 'phone': ''}
        self.client.post(self.url, data=invalid_data)
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_failure_does_not_break_form_submission(self):
        with patch('common.notifications.send_mail', side_effect=Exception('SMTP down')):
            response = self.client.post(self.url, data=self.valid_data)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(ConsultationRequest.objects.filter(email='client@example.com').exists())


class ConsultationCreateViewTest(TestCase):
    def setUp(self):
        self.url = reverse('main:new-consultation')

    def test_get_consultation_page_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_consultation_page_has_form_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    def test_valid_post_creates_consultation_request(self):
        self.assertEqual(ConsultationRequest.objects.count(), 0)
        self.client.post(self.url, data=build_valid_data())
        self.assertEqual(ConsultationRequest.objects.count(), 1)

    def test_valid_post_redirects_to_home(self):
        response = self.client.post(self.url, data=build_valid_data())
        self.assertRedirects(response, reverse('main:home'))

    def test_valid_post_has_success_message(self):
        response = self.client.post(self.url, data=build_valid_data(), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('успешно отправлена' in str(m) for m in messages))

    def test_invalid_post_does_not_create_request(self):
        data = build_valid_data()
        data['phone'] = 'invalid'
        self.client.post(self.url, data=data)
        self.assertEqual(ConsultationRequest.objects.count(), 0)

    def test_invalid_post_returns_form_with_errors(self):
        data = build_valid_data()
        data['phone'] = 'invalid'
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


class MainPagesTest(TestCase):
    def test_home_page_returns_200(self):
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_returns_200(self):
        response = self.client.get(reverse('main:about'))
        self.assertEqual(response.status_code, 200)

    def test_consultation_page_shows_manual_processing_disclaimer(self):
        response = self.client.get(reverse('main:new-consultation'))

        self.assertContains(response, 'обработка заявок не автоматизирована')
        self.assertContains(response, 'в течение одного рабочего дня')

    def test_contacts_page_returns_200(self):
        response = self.client.get(reverse('main:contacts'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_page_contains_actual_contact_information(self):
        response = self.client.get(reverse('main:contacts'))

        self.assertContains(response, '0312 214015')
        self.assertContains(response, 'г. Бишкек, ул. Юдахина 61')
        self.assertContains(response, '+996 555 922 604')
        self.assertContains(response, 'palliativecare_kg')
        self.assertContains(response, 'https://www.facebook.com/palliativecare.kg')
        self.assertContains(response, 'https://2gis.kg/bishkek/geo/70000001117702816')
