from unittest.mock import patch

import requests
from django.test import SimpleTestCase

from common.turnstile import verify_turnstile_token


class TurnstileVerificationTestCase(SimpleTestCase):
    @patch("common.turnstile.requests.post")
    def test_verify_token_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        result = verify_turnstile_token("valid_token")
        self.assertTrue(result)
    @patch("common.turnstile.requests.post")
    def test_verify_token_invalid(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": False}
        result = verify_turnstile_token("invalid_token")
        self.assertFalse(result)

    @patch("common.turnstile.requests.post")
    def test_verify_token_server_error_fail_open(self, mock_post):
        mock_post.return_value.status_code = 500
        with self.assertLogs("common.turnstile", level="WARNING") as log:
            result = verify_turnstile_token("any_token")
            self.assertTrue(result)
            self.assertIn("Ошибка сервера Cloudflare Turnstile", log.output[0])

    @patch("common.turnstile.requests.post")
    def test_verify_token_network_exception_fail_open(self, mock_post):
        mock_post.side_effect = requests.RequestException("Timeout")
        with self.assertLogs("common.turnstile", level="WARNING") as log:
            result = verify_turnstile_token("any_token")
            self.assertTrue(result)
            self.assertIn("Сбой подключения к Cloudflare Turnstile", log.output[0])
