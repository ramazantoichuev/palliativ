from django.test import TestCase

from main.forms import ConsultationForm


def build_form_data(phone):
    return {
        'first_name': 'Айгуль',
        'phone': phone,
        'email': 'test@example.com',
        'topic': 'medical_help',
    }


class ConsultationFormMobileNumbersTests(TestCase):

    def test_valid_mobile_numbers_by_operator_code(self):
        valid_codes = ['50', '51', '52', '54', '55', '56', '57', '70', '75', '77', '99', '22']

        for code in valid_codes:
            with self.subTest(operator_code=code):
                phone = f'0{code}1234567'
                form = ConsultationForm(data=build_form_data(phone))

                is_valid = form.is_valid()

                self.assertTrue(is_valid, form.errors)
                self.assertEqual(form.cleaned_data['phone'], f'+996{code}1234567')

    def test_mobile_number_with_plus_996_format_is_valid(self):
        form = ConsultationForm(data=build_form_data('+996555123456'))

        is_valid = form.is_valid()

        self.assertTrue(is_valid, form.errors)
        self.assertEqual(form.cleaned_data['phone'], '+996555123456')

    def test_mobile_number_with_spaces_and_dashes_is_normalized(self):
        form = ConsultationForm(data=build_form_data('0 555-123-456'))

        is_valid = form.is_valid()

        self.assertTrue(is_valid, form.errors)
        self.assertEqual(form.cleaned_data['phone'], '+996555123456')

    def test_unknown_operator_code_is_invalid(self):
        form = ConsultationForm(data=build_form_data('0123456789'))

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertIn('phone', form.errors)


class ConsultationFormLandlineNumbersTests(TestCase):

    def test_bishkek_landline_number_is_valid(self):
        form = ConsultationForm(data=build_form_data('0312555123'))

        is_valid = form.is_valid()

        self.assertTrue(is_valid, form.errors)
        self.assertEqual(form.cleaned_data['phone'], '+996312555123')

    def test_oblast_center_landline_numbers_are_valid(self):
        oblast_codes = {
            '3222': 'Ош',
            '3422': 'Талас',
            '3522': 'Нарын',
            '3622': 'Баткен',
            '3722': 'Джалал-Абад',
            '3922': 'Каракол',
        }

        for code, city in oblast_codes.items():
            with self.subTest(city=city, code=code):
                phone = f'0{code}12345'
                form = ConsultationForm(data=build_form_data(phone))

                is_valid = form.is_valid()

                self.assertTrue(is_valid, form.errors)
                self.assertEqual(form.cleaned_data['phone'], f'+996{code}12345')

    def test_landline_number_with_wrong_length_is_invalid(self):
        form = ConsultationForm(data=build_form_data('032221234'))
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertIn('phone', form.errors)

    def test_unrecognized_city_code_is_invalid(self):
        form = ConsultationForm(data=build_form_data('0399912345'))

        # Act
        is_valid = form.is_valid()

        # Assert
        self.assertFalse(is_valid)
        self.assertIn('phone', form.errors)


class ConsultationFormGeneralValidationTests(TestCase):

    def test_missing_first_name_is_invalid(self):
        data = build_form_data('0555123456')
        data['first_name'] = ''
        form = ConsultationForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertIn('first_name', form.errors)

    def test_invalid_email_is_invalid(self):
        data = build_form_data('0555123456')
        data['email'] = 'not-an-email'
        form = ConsultationForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertIn('email', form.errors)

    def test_invalid_topic_choice_is_invalid(self):
        data = build_form_data('0555123456')
        data['topic'] = 'not_a_real_topic'
        form = ConsultationForm(data=data)

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertIn('topic', form.errors)