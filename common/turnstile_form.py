from django import forms
from django.utils.translation import gettext_lazy as _

from common.turnstile import verify_turnstile_token


class TurnstileFormMixin:
    data: dict
    def clean(self):
        cleaned_data = super().clean()
        turnstile_token = self.data.get('cf-turnstile-response')

        if not verify_turnstile_token(turnstile_token):
            raise forms.ValidationError(
                _("Ошибка проверки безопасности. Пожалуйста, попробуйте еще раз.")
            )
        return cleaned_data
