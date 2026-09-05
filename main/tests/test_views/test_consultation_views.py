from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from main.models.consultation import ConsultationRequest


def build_valid_data():
    return {
        'first_name': 'Айгуль',
        'phone': '0555123456',
        'email': 'test@example.com',
        'topic': 'medical_help',
    }


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
        response = self.client.post(self.url, data=build_valid_data())
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

    def test_contacts_page_returns_200(self):
        response = self.client.get(reverse('main:contacts'))
        self.assertEqual(response.status_code, 200)
