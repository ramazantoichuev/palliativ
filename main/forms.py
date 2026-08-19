import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models.consultation import ConsultationRequest


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['first_name', 'phone', 'email', 'topic']
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if digits.startswith('0') and len(digits) == 10:
            digits = '996' + digits[1:]
        elif digits.startswith('996') and len(digits) == 12:
            pass
        else:
            raise ValidationError(
                _('Неверный формат номера. Введите номер в формате: 0555123456 или +996555123456')
            )
        operator_code = digits[3:6]
        valid_codes = {
            '50', '51', '52', '54', '55', '56', '57', '70', '75', '77', '99', '22'
        }
        if operator_code[:2] not in valid_codes:
            raise ValidationError(
                _('Неверный код оператора Кыргызстана. Проверьте правильность ввода.')
            )
        return f"+{digits}"
