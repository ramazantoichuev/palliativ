from django.test import RequestFactory, SimpleTestCase

from common.utils import get_client_ip


class GetClientIpTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_prefers_x_real_ip(self):
        request = self.factory.get(
            "/", HTTP_X_REAL_IP="1.2.3.4", REMOTE_ADDR="10.0.0.1"
        )
        self.assertEqual(get_client_ip(request), "1.2.3.4")

    def test_falls_back_to_remote_addr(self):
        request = self.factory.get("/", REMOTE_ADDR="10.0.0.1")
        self.assertEqual(get_client_ip(request), "10.0.0.1")

    def test_ignores_x_forwarded_for(self):
        request = self.factory.get(
            "/", HTTP_X_FORWARDED_FOR="6.6.6.6", REMOTE_ADDR="10.0.0.1"
        )
        self.assertEqual(get_client_ip(request), "10.0.0.1")