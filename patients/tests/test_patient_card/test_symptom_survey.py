from django.test import TestCase
from django.urls import reverse

from accounts.models import BaseUser
from patients.models import PatientCard, Symptom


class SymptomSurveyViewTests(TestCase):
    def setUp(self):
        self.patient_user = BaseUser.objects.create_user(
            username='test_patient',
            password='password123',
            email='test_patient@example.com',
            phone='+996555123455',
            role=BaseUser.Role.PATIENT,
        )
        self.patient_profile = self.patient_user.patient_profile

        self.symptom_pain = Symptom.objects.create(name='Боль')
        self.symptom_fever = Symptom.objects.create(name='Жар')
        self.symptom_cough = Symptom.objects.create(name='Кашель')

        self.card = PatientCard.objects.create(
            patient=self.patient_profile,
            diagnosis='Основной диагноз',
            medications='Препараты',
            contraindications='Противопоказания',
        )

        self.url = reverse('patients:symptom_survey')
        self.dashboard_url = reverse('patients:patient_dashboard')

    def test_patient_can_open_survey(self):
        self.client.force_login(self.patient_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Как вы себя чувствуете?')

    def test_patient_can_save_symptoms(self):
        self.client.force_login(self.patient_user)

        response = self.client.post(
            self.url,
            {'symptoms': [self.symptom_pain.id, self.symptom_cough.id]},
        )

        self.assertRedirects(response, self.dashboard_url)
        self.assertEqual(
            set(self.card.symptoms.all()),
            {self.symptom_pain, self.symptom_cough},
        )

    def test_selected_symptoms_are_prefilled(self):
        self.card.symptoms.add(
            self.symptom_pain,
            self.symptom_cough,
        )

        self.client.force_login(self.patient_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertIn(self.symptom_pain, form.initial['symptoms'])
        self.assertIn(self.symptom_cough, form.initial['symptoms'])
        self.assertNotIn(self.symptom_fever, form.initial['symptoms'])

    def test_empty_post_clears_symptoms(self):
        self.card.symptoms.add(
            self.symptom_pain,
            self.symptom_cough,
        )

        self.client.force_login(self.patient_user)

        response = self.client.post(self.url, {})

        self.assertRedirects(response, self.dashboard_url)
        self.assertEqual(self.card.symptoms.count(), 0)

    def test_non_patient_cannot_open_survey(self):
        doctor_user = BaseUser.objects.create_user(
            username='test_doctor',
            password='password123',
            email='test_doctor@example.com',
            phone='+996555123456',
            role=BaseUser.Role.DOCTOR,
        )

        self.client.force_login(doctor_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_open_survey(self):
        manager_user = BaseUser.objects.create_user(
            username='test_manager',
            password='password123',
            email='test_manager@example.com',
            phone='+996555123458',
            role=BaseUser.Role.MANAGER,
        )
        self.client.force_login(manager_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_patient_without_card_is_redirected_to_dashboard(self):
        patient_user = BaseUser.objects.create_user(
            username='patient_without_card',
            password='password123',
            email='patient_without_card@example.com',
            phone='+996555123457',
            role=BaseUser.Role.PATIENT,
        )

        self.client.force_login(patient_user)

        response = self.client.get(self.url)

        self.assertRedirects(response, self.dashboard_url)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn(
            'Карточка ещё не заведена',
            str(messages[0]),
        )

    def test_only_latest_card_is_updated(self):
        old_card = self.card

        new_card = PatientCard.objects.create(
            patient=self.patient_profile,
            diagnosis='Новый диагноз',
        )

        self.client.force_login(self.patient_user)

        response = self.client.post(
            self.url,
            {'symptoms': [self.symptom_pain.id]},
        )

        self.assertRedirects(response, self.dashboard_url)

        old_card.refresh_from_db()
        new_card.refresh_from_db()

        self.assertEqual(old_card.symptoms.count(), 0)
        self.assertEqual(new_card.symptoms.count(), 1)
        self.assertIn(
            self.symptom_pain,
            new_card.symptoms.all(),
        )

    def test_extra_post_fields_are_ignored(self):
        self.client.force_login(self.patient_user)

        response = self.client.post(
            self.url,
            {
                'symptoms': [self.symptom_pain.id],
                'diagnosis': 'Измененный диагноз',
                'medications': 'Измененные препараты',
                'contraindications': 'Измененные противопоказания',
                'doctor': '',
            },
        )

        self.assertRedirects(response, self.dashboard_url)

        self.card.refresh_from_db()

        self.assertEqual(
            self.card.diagnosis,
            'Основной диагноз',
        )
        self.assertEqual(
            self.card.medications,
            'Препараты',
        )
        self.assertEqual(
            self.card.contraindications,
            'Противопоказания',
        )
        self.assertIsNone(self.card.doctor)
        self.assertIn(
            self.symptom_pain,
            self.card.symptoms.all(),
        )
