from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.tests.factories import UserFactory

User = get_user_model()


class TestPatientRegisterView(TestCase):
    def setUp(self):
        super().setUp()
        self.turnstile_patcher = mock.patch(
            "common.turnstile_form.verify_turnstile_token", return_value=True
        )
        self.turnstile_patcher.start()

    def tearDown(self):
        self.turnstile_patcher.stop()
        super().tearDown()

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_get_patient_register_view(self):
        url = reverse("accounts:patient_register")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/patient_register.html")
        self.assertIn("form", response.context)

    @mock.patch("accounts.views.login")
    def test_post_patient_register_view_success(self, mocked_login: mock.MagicMock):
        url = reverse("accounts:patient_register")
        response = self.client.post(
            url,
            data={
                "email": "test@mail.ru",
                "first_name": "John",
                "last_name": "Doe",
                "password1": "1qaz@WSX29",
                "password2": "1qaz@WSX29",
                "phone": "+996700123456",
                "cf-turnstile-response": "dummy_token",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(first_name="John").exists())
        mocked_login.assert_called_once()

    @mock.patch("accounts.views.login")
    def test_post_patient_register_view_fail(self, mocked_login: mock.MagicMock):
        url = reverse("accounts:patient_register")
        response = self.client.post(
            url,
            data={
                "email": "invalid@mail.ru",
                "first_name": "Jane",
                "last_name": "Doe",
                "password1": "1qaz@WSX29",
                "password2": "different",
                "phone": "+996700123457",
                "cf-turnstile-response": "dummy_token",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="invalid@mail.ru").exists())
        mocked_login.assert_not_called()

    @override_settings(NOTIFICATION_EMAILS=['admin@example.com'])
    @mock.patch('accounts.views.login')
    def test_post_patient_register_view_sends_admin_notification(self, mocked_login: mock.MagicMock):
        # Arrange
        url = reverse('accounts:patient_register')
        data = {
            "email": "notify_patient@mail.ru",
            "first_name": "Aigerim",
            "last_name": "Test",
            "password1": "1qaz@WSX29",
            "password2": "1qaz@WSX29",
            "phone": "+996700123458",
            "cf-turnstile-response": "dummy_token",
        }

        # Act
        self.client.post(url, data=data)

        # Assert
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('notify_patient@mail.ru', mail.outbox[0].body)

    def test_invalid_turnstile_does_not_create_user(self):
        url = reverse("accounts:patient_register")
        with mock.patch("common.turnstile_form.verify_turnstile_token", return_value=False):
            response = self.client.post(
                url,
                data={
                    "email": "bad_turnstile@mail.ru",
                    "first_name": "Bad",
                    "last_name": "Turnstile",
                    "password1": "1qaz@WSX29",
                    "password2": "1qaz@WSX29",
                    "phone": "+996700123460",
                    "cf-turnstile-response": "bad_token",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="bad_turnstile@mail.ru").exists())

    @override_settings(NOTIFICATION_EMAILS=['admin@example.com'])
    def test_post_invalid_patient_register_does_not_send_email(self):
        # Arrange
        url = reverse('accounts:patient_register')
        data = {
            "email": "invalid_notify@mail.ru",
            "first_name": "Jane",
            "last_name": "Doe",
            "password1": "1qaz@WSX29",
            "password2": "different",
            "phone": "+996700123459",
            "cf-turnstile-response": "dummy_token",
        }

        self.client.post(url, data=data)

        self.assertEqual(len(mail.outbox), 0)
