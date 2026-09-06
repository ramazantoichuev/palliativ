import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models.consultation import ConsultationRequest

BISHKEK_CODE = '312'
OBLAST_CENTER_CODES = {'3222', '3422', '3522', '3622', '3722', '3922'}


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['first_name', 'phone', 'email', 'topic']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if digits.startswith('0'):
            digits = '996' + digits[1:]
        if not digits.startswith('996') or len(digits) != 12:
            raise ValidationError(
                _('Неверный формат номера. Введите номер в формате: '
                  '0555123456 (мобильный) или 0312123456 (городской, Бишкек)')
            )

        national = digits[3:]  # ровно 9 цифр

        mobile_codes = {'50', '51', '52', '54', '55', '56', '57', '70', '75', '77', '99', '22'}
        is_mobile = national[:2] in mobile_codes
        is_bishkek = national[:3] == BISHKEK_CODE
        is_oblast_center = national[:4] in OBLAST_CENTER_CODES

        if not (is_mobile or is_bishkek or is_oblast_center):
            raise ValidationError(
                _('Неверный код оператора или города. Проверьте правильность ввода '
                  'номера мобильного или городского телефона Кыргызстана.')
            )

        return f"+{digits}"