from django.test import TestCase

from accounts.models import BaseUser, PatientProfile
from patients.models import PatientCard, Symptom
from resources.models.resources import Resource


class SymptomMatchingSimpleTest(TestCase):
    def setUp(self):
        self.patient_user = BaseUser.objects.create_user(
            username='test_patient', password='password123', role=BaseUser.Role.PATIENT
        )
        self.patient_profile, _ = PatientProfile.objects.get_or_create(user=self.patient_user)
        self.symptom_pain = Symptom.objects.create(name="Боль")
        self.symptom_fever = Symptom.objects.create(name="Жар")
        self.symptom_cough = Symptom.objects.create(name="Кашель")
        self.resource_pain = Resource.objects.create(title="Инструкция при боли")
        self.resource_pain.symptoms.add(self.symptom_pain)
        self.resource_fever = Resource.objects.create(title="Инструкция при жаре")
        self.resource_fever.symptoms.add(self.symptom_fever)
        self.resource_cough = Resource.objects.create(title="Инструкция при кашле")
        self.resource_cough.symptoms.add(self.symptom_cough)
        self.card = PatientCard.objects.create(
            patient=self.patient_profile,
            diagnosis="Первичный осмотр"
        )

    def test_matching_resources_by_symptom(self):
        self.card.symptoms.add(self.symptom_pain)
        matching_resources = list(self.card.get_matching_resources())
        self.assertIn(self.resource_pain, matching_resources)
        self.assertNotIn(self.resource_fever, matching_resources)
        self.assertNotIn(self.resource_cough, matching_resources)

    def test_empty_symptoms_returns_empty_result(self):
        matching_resources = self.card.get_matching_resources()
        self.assertEqual(len(matching_resources), 0)