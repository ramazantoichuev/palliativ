from django.test import TestCase
from django.urls import reverse

from accounts.tests.factories import User


class TestDoctorRegisterView(TestCase):

    def test_get_doctor_register_view(self):
        url = reverse('accounts:doctor_register')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/doctor_register.html')
        self.assertIn('form', response.context)

    def test_post_doctor_register_view_success(self):
        url = reverse('accounts:doctor_register')
        response = self.client.post(url, data={
                "email": "doctor@test.kg",
                "first_name": "Марат",
                "last_name": "Иманалиев",
                "password1": "1qaz@WSX29",
                "password2": "1qaz@WSX29",
                "phone": "+996700000070",
                "education": "КГМА, лечебное дело",
                "skills": "Паллиативная помощь",})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/doctor_application_sent.html')

        user = User.objects.get(email="doctor@test.kg")
        self.assertFalse(user.is_approved)

    def test_doctor_not_logged_in_after_registration(self):
        url = reverse('accounts:doctor_register')
        self.client.post(url, data={
            "email": "doctor@test.kg",
            "first_name": "Марат",
            "last_name": "Иманалиев",
            "password1": "1qaz@WSX29",
            "password2": "1qaz@WSX29",
            "phone": "+996700000070",
            "education": "КГМА, лечебное дело",
            "skills": "Паллиативная помощь", })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_post_invalid_data_does_not_create_user(self):
        url = reverse('accounts:doctor_register')
        response = self.client.post(
            url,
            data={
                "email": "doctor3@test.kg",
                "first_name": "Врач",
                "last_name": "Третий",
                "password1": "1qaz@WSX29",
                "password2": "different",
                "phone": "+996700000072",
                "education": "Мед",
                "skills": "Уход",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="doctor3@test.kg").exists())