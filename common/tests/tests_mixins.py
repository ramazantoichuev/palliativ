from unittest.mock import patch

import requests


class FormTurnstileIntegrationMixin:
    """
    Общий миксин для тестов Django-форм с защитой Turnstile.
    """
    form_class: type
    base_form_data: dict
    turnstile_patch_path: str

    def test_form_validation_with_valid_turnstile(self):
        with patch(self.turnstile_patch_path) as mock_verify:
            mock_verify.return_value = True
            data = {
                **self.base_form_data,
                "cf-turnstile-response": "valid_token",
            }
            form = self.form_class(data=data)
            self.assertTrue(form.is_valid())
            mock_verify.assert_called_once_with("valid_token")

    def test_form_validation_fails_with_invalid_turnstile(self):
        with patch(self.turnstile_patch_path) as mock_verify:
            mock_verify.return_value = False
            data = {
                **self.base_form_data,
                "cf-turnstile-response": "bad_token",
            }
            form = self.form_class(data=data)
            self.assertFalse(form.is_valid())
            errors = " ".join(form.errors.get("__all__", []))
            self.assertIn("Ошибка проверки безопасности", errors)

    def test_form_validation_passes_when_service_unavailable_fail_open(self):
        with patch("common.turnstile.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Timeout")
            data = {
                **self.base_form_data,
                "cf-turnstile-response": "any_token",
            }
            form = self.form_class(data=data)
            self.assertTrue(form.is_valid())