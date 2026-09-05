from django.test import TestCase
from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory
from resources.tests.factories import SymptomFactory

class ResourceModelTest(TestCase):
    def test_str_returns_title(self):
        resource = ResourceFactory(title='Уход при боли')
        self.assertEqual(str(resource), 'Уход при боли')

    def test_audience_choices(self):
        resource = ResourceFactory(audience=Resource.AUDIENCE_CAREGIVER)
        self.assertEqual(resource.audience, 'caregiver')

    def test_subcategory_choices(self):
        resource = ResourceFactory(subcategory='npa')
        self.assertEqual(resource.subcategory, 'npa')

    def test_symptoms_relation(self):
        symptom = SymptomFactory(name='Боль')
        resource = ResourceFactory(symptoms=[symptom])
        self.assertIn(symptom, resource.symptoms.all())
