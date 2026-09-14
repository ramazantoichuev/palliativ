from django.test import TestCase

from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory, SymptomFactory


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


class ResourceGetAbsoluteUrlTests(TestCase):
    def test_get_absolute_url_returns_correct_path(self):
        resource = Resource.objects.create(
            title="Тестовый материал",
            audience="caregiver",
            subcategory="care_feeding",
        )

        url = resource.get_absolute_url()

        self.assertEqual(url, f"/resources/{resource.slug}/")
