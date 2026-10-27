from django.test import TestCase
from django.urls import reverse

from accounts.tests.factories import UserFactory
from common.tests.tests_mixins import RateLimitCacheResetMixin
from main.models.system_settings import SystemSettings


class NavLoginLinkTests(RateLimitCacheResetMixin, TestCase):
    """Кнопка «Войти» в шапке скрыта, когда выключены обе регистрации (Ticket 117).

    Маркер — точный href ссылки меню: на главной адреса страницы входа
    нет ни в canonical, ни в og:url, ложных срабатываний не будет.
    """

    nav_login_marker = 'href="/accounts/login/"'

    def setUp(self):
        super().setUp()
        self.home_url = reverse("main:home")

    @staticmethod
    def set_registrations(patient, doctor):
        SystemSettings.objects.create(
            patient_registration_enabled=patient,
            doctor_registration_enabled=doctor,
        )

    def test_login_link_shown_when_both_registrations_enabled(self):
        self.set_registrations(patient=True, doctor=True)

        response = self.client.get(self.home_url)

        self.assertContains(response, self.nav_login_marker)

    def test_login_link_shown_when_only_patient_registration_enabled(self):
        self.set_registrations(patient=True, doctor=False)

        response = self.client.get(self.home_url)

        self.assertContains(response, self.nav_login_marker)

    def test_login_link_shown_when_only_doctor_registration_enabled(self):
        self.set_registrations(patient=False, doctor=True)

        response = self.client.get(self.home_url)

        self.assertContains(response, self.nav_login_marker)

    def test_login_link_hidden_when_both_registrations_disabled(self):
        self.set_registrations(patient=False, doctor=False)

        response = self.client.get(self.home_url)

        self.assertNotContains(response, self.nav_login_marker)
        # остальные пункты меню на месте
        self.assertContains(response, 'href="/about/"')
        self.assertContains(response, 'href="/contacts/"')

    def test_logged_in_user_sees_logout_not_login_when_both_disabled(self):
        self.set_registrations(patient=False, doctor=False)
        self.client.force_login(UserFactory())

        response = self.client.get(self.home_url)

        self.assertContains(response, 'action="/accounts/logout/"')
        self.assertNotContains(response, self.nav_login_marker)

    def test_login_page_and_authentication_work_when_both_disabled(self):
        self.set_registrations(patient=False, doctor=False)
        user = UserFactory(password="testpass123")

        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("accounts:login"),
            {"username": user.email, "password": "testpass123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
