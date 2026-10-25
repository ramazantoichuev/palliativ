from django.test import TestCase

from patients.matching import match_resources
from patients.models import Symptom
from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory

SPEC = Resource.AUDIENCE_SPECIALIST
CARE = Resource.AUDIENCE_CAREGIVER
PED = Resource.AUDIENCE_PEDIATRIC


class MatchResourcesTests(TestCase):
    def setUp(self):
        self.pain = Symptom.objects.create(name="Боль")
        self.fever = Symptom.objects.create(name="Жар")
        self.spec = self._res(SPEC, self.pain)
        self.care = self._res(CARE, self.pain)
        self.ped = self._res(PED, self.pain)

    def _res(self, audience, *symptoms):
        resource = ResourceFactory(audience=audience)
        resource.symptoms.add(*symptoms)
        return resource

    def _titles(self, groups, symptom):
        group = next(g for g in groups if g["symptom"] == symptom)
        return set(group["resources"])

    def test_adult_doctor_gets_specialist_and_caregiver(self):
        groups = match_resources([self.pain], for_doctor=True, is_child=False)
        self.assertEqual(self._titles(groups, self.pain), {self.spec, self.care})

    def test_adult_patient_gets_only_caregiver(self):
        groups = match_resources([self.pain], for_doctor=False, is_child=False)
        self.assertEqual(self._titles(groups, self.pain), {self.care})

    def test_child_doctor_gets_specialist_and_pediatric(self):
        groups = match_resources([self.pain], for_doctor=True, is_child=True)
        self.assertEqual(self._titles(groups, self.pain), {self.spec, self.ped})

    def test_child_patient_gets_only_pediatric(self):
        groups = match_resources([self.pain], for_doctor=False, is_child=True)
        self.assertEqual(self._titles(groups, self.pain), {self.ped})

    def test_resource_without_symptom_match_is_in_no_group(self):
        other = self._res(CARE)  # без симптомов
        groups = match_resources([self.pain], for_doctor=False, is_child=False)
        for group in groups:
            self.assertNotIn(other, group["resources"])

    def test_symptom_without_resources_gives_empty_group(self):
        groups = match_resources([self.fever], for_doctor=False, is_child=False)
        self.assertEqual(groups[0]["resources"], [])

    def test_resource_appears_in_each_matching_symptom_group(self):
        shared = self._res(CARE, self.pain, self.fever)
        groups = match_resources([self.pain, self.fever], for_doctor=False, is_child=False)
        self.assertIn(shared, self._titles(groups, self.pain))
        self.assertIn(shared, self._titles(groups, self.fever))