from django.db import transaction
from django.test import TestCase

from accounts.tests.factories import User, UserFactory
from patients.models import PatientCard, Symptom


class PatientCardModelTests(TestCase):

    def _patient_profile(self):
        return UserFactory(role=User.Role.PATIENT).patient_profile

    def _doctor_profile(self):
        return UserFactory(role=User.Role.DOCTOR).doctor_profile

    def test_related_name_medical_cards_on_patient(self):
        patient = self._patient_profile()
        card = PatientCard.objects.create(patient=patient, diagnosis="Диагноз")
        self.assertIn(card, patient.medical_cards.all())

    def test_related_name_assigned_cards_on_doctor(self):
        patient = self._patient_profile()
        doctor = self._doctor_profile()
        card = PatientCard.objects.create(patient=patient, doctor=doctor, diagnosis="Диагноз")
        self.assertIn(card, doctor.assigned_cards.all())

    def test_symptoms_many_to_many(self):
        patient = self._patient_profile()
        card = PatientCard.objects.create(patient=patient, diagnosis="Диагноз")
        s1 = Symptom.objects.create(name="Тошнота")
        s2 = Symptom.objects.create(name="Слабость")

        card.symptoms.add(s1, s2)

        self.assertEqual(card.symptoms.count(), 2)
        self.assertIn(s1, card.symptoms.all())

    def test_card_deleted_when_patient_deleted(self):
        patient = self._patient_profile()
        card = PatientCard.objects.create(patient=patient, diagnosis="Диагноз")
        card_id = card.id

        patient.user.delete()

        self.assertFalse(PatientCard.objects.filter(id=card_id).exists())