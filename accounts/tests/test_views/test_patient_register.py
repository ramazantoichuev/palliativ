from unittest import mock

from django.contrib.auth import get_user_model
from django.template.defaultfilters import last
from django.test import TestCase
from django.urls import reverse

from accounts.tests.factories import UserFactory

User = get_user_model()


class TestPatientRegisterView(TestCase):

    @classmethod
    def setUpTestData(cls):
        # User.objects.create(
        #     first_name="John",
        #     last_name="Doe",
        # )
        cls.user = UserFactory()

    def test_get_patient_register_view(self):
        url = reverse('accounts:patient_register')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/patient_register.html')
        self.assertIn("form", response.context)

    @mock.patch('accounts.views.login')
    def test_post_patient_register_view_success(self, mocked_login: mock.MagicMock):
        url = reverse('accounts:patient_register')
        response = self.client.post(
            url,
            data={
                "email": "test@mail.ru",
                "first_name": "John",
                "last_name": "Doe",
                "password1": "1qaz@WSX29",
                "password2": "1qaz@WSX29",
                "phone": "+996700123456"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(first_name="John").exists()
        )
        mocked_login.assert_called_once()

    def test_post_patient_register_view_fail(self):
        pass
