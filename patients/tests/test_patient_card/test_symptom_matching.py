from django.test import TestCase

from accounts.models import BaseUser, PatientProfile
from patients.models import PatientCard, Symptom
from resources.models.resources import Resource


class SymptomMatchingSimpleTest(TestCase):
    def setUp(self):
        self.patient_user = BaseUser.objects.create_user(
            username="test_patient", password="password123", role=BaseUser.Role.PATIENT
        )
        self.patient_profile, _ = PatientProfile.objects.get_or_create(
            user=self.patient_user
        )
        self.symptom_pain = Symptom.objects.create(name="Боль")
        self.symptom_fever = Symptom.objects.create(name="Жар")
        self.symptom_cough = Symptom.objects.create(name="Кашель")
        self.resource_pain = self._resource("Инструкция при боли", self.symptom_pain)
        self.resource_fever = self._resource("Инструкция при жаре", self.symptom_fever)
        self.resource_cough = self._resource("Инструкция при кашле", self.symptom_cough)
        self.card = PatientCard.objects.create(
            patient=self.patient_profile, diagnosis="Первичный осмотр"
        )

    def _resource(self, title, symptom):
        resource = Resource.objects.create(
            title=title, audience=Resource.AUDIENCE_CAREGIVER
        )
        resource.symptoms.add(symptom)
        return resource

    def _all_resources(self):
        return [r for g in self.card.get_resource_groups() for r in g["resources"]]

    def test_matching_resources_by_symptom(self):
        self.card.symptoms.add(self.symptom_pain)
        matching_resources = self._all_resources()
        self.assertIn(self.resource_pain, matching_resources)
        self.assertNotIn(self.resource_fever, matching_resources)
        self.assertNotIn(self.resource_cough, matching_resources)

    def test_empty_symptoms_returns_empty_result(self):
        self.assertEqual(self.card.get_resource_groups(), [])
