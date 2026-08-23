from django.test import RequestFactory, TestCase

from accounts.forms import EmailAuthenticationForm
from accounts.tests.factories import UserFactory


class EmailAuthenticationFormTests(TestCase):

    def setUp(self):
        self.request = RequestFactory().post("/accounts/login/")
        self.password = "strongpass1"
        self.user = UserFactory(email="login@test.kg")
        self.user.set_password(self.password)
        self.user.save()

    def test_valid_credentials(self):
        form = EmailAuthenticationForm(
            self.request,
            data={"username": "login@test.kg", "password": self.password},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_wrong_password_is_invalid(self):
        form = EmailAuthenticationForm(
            self.request,
            data={"username": "login@test.kg", "password": "wrongpass"},
        )
        self.assertFalse(form.is_valid())