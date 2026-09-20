from django.test import TestCase

from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory, SymptomFactory, TermFactory


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

    def test_resource_with_terms_renders_popover_buttons(self):
        term = TermFactory(name='Агевзия', definition='Потеря вкусовой чувствительности')
        resource = ResourceFactory()
        resource.terms.add(term)

        response = self.client.get(resource.get_absolute_url())

        self.assertContains(response, 'Агевзия')
        self.assertContains(response, 'data-bs-toggle="popover"')

    def test_resource_without_terms_renders_normally(self):
        resource = ResourceFactory()
        response = self.client.get(resource.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class ResourceGetAbsoluteUrlTests(TestCase):
    def test_get_absolute_url_returns_correct_path(self):
        resource = Resource.objects.create(
            title="Тестовый материал",
            audience="caregiver",
            subcategory="care_feeding",
        )

        url = resource.get_absolute_url()

        self.assertEqual(url, f"/resources/{resource.slug}/")
