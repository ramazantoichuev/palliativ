from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from main.models.consultation import ConsultationRequest


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
        from unittest.mock import patch

        with patch('common.notifications.send_mail', side_effect=Exception('SMTP down')):
            response = self.client.post(self.url, data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ConsultationRequest.objects.filter(email='client@example.com').exists())