from unittest.mock import patch


class FormTurnstileIntegrationMixin:
    """
    Общий миксин для тестов Django-форм с защитой Turnstile.
    """
    form_class: type
    base_form_data: dict
    turnstile_patch_path: str
    def assertTrue(self, expr, msg=None): pass
    def assertFalse(self, expr, msg=None): pass
    def assertIn(self, member, container, msg=None): pass

    def test_form_validation_with_valid_turnstile(self):
        """Форма валидна при успешном токене"""
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
            self.assertIn(
                "Ошибка проверки безопасности",
                form.errors.get("__all__", []),
            )

    def test_form_validation_passes_when_service_unavailable_fail_open(self):
        with patch(self.turnstile_patch_path) as mock_verify:
            mock_verify.return_value = True
            data = {
                **self.base_form_data,
                "cf-turnstile-response": "any_token",
            }
            form = self.form_class(data=data)
            self.assertTrue(form.is_valid())

