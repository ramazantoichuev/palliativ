from django.test import TestCase
from django.urls import reverse
from resources.models.resources import Resource
from resources.tests.factories import ResourceFactory, SymptomFactory


class ResourceListViewTest(TestCase):
    def setUp(self):
        self.url = reverse('resources:resource_list')
        self.symptom_pain = SymptomFactory(name='Боль')
        self.symptom_fever = SymptomFactory(name='Жар')

    def test_list_returns_200(self):
        ResourceFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_materials_displayed(self):
        resource = ResourceFactory(title='Тестовый материал')
        response = self.client.get(self.url)
        self.assertContains(response, 'Тестовый материал')

    def test_filter_by_audience(self):
        specialist_resource = ResourceFactory(audience=Resource.AUDIENCE_SPECIALIST, title='Для специалиста')
        caregiver_resource = ResourceFactory(audience=Resource.AUDIENCE_CAREGIVER, title='Для ухаживающего')

        response = self.client.get(self.url, {'audience': Resource.AUDIENCE_SPECIALIST})

        self.assertContains(response, 'Для специалиста')
        self.assertNotContains(response, 'Для ухаживающего')

    def test_filter_by_subcategory(self):
        target = ResourceFactory(subcategory='npa', title='НПА материал')
        other = ResourceFactory(subcategory='care_feeding', title='Уход материал')

        response = self.client.get(self.url, {'subcategory': 'npa'})

        self.assertContains(response, 'НПА материал')
        self.assertNotContains(response, 'Уход материал')

    def test_filter_by_symptom(self):
        target = ResourceFactory(title='С болью', symptoms=[self.symptom_pain])
        other = ResourceFactory(title='С жаром', symptoms=[self.symptom_fever])

        response = self.client.get(self.url, {'symptom': self.symptom_pain.id})

        self.assertContains(response, 'С болью')
        self.assertNotContains(response, 'С жаром')

    def test_combined_filters(self):
        target = ResourceFactory(
            audience=Resource.AUDIENCE_SPECIALIST,
            subcategory='symptom_control',
            symptoms=[self.symptom_pain],
            title='Подходящий'
        )
        wrong_audience = ResourceFactory(
            audience=Resource.AUDIENCE_CAREGIVER,
            subcategory='symptom_control',
            symptoms=[self.symptom_pain],
            title='Не та аудитория'
        )

        response = self.client.get(self.url, {
            'audience': Resource.AUDIENCE_SPECIALIST,
            'subcategory': 'symptom_control',
            'symptom': self.symptom_pain.id,
        })

        self.assertContains(response, 'Подходящий')
        self.assertNotContains(response, 'Не та аудитория')

    def test_nonexistent_symptom_filter_not_500(self):
        response = self.client.get(self.url, {'symptom': 999})
        self.assertEqual(response.status_code, 200)

    def test_empty_result_correct_state(self):
        response = self.client.get(self.url, {'subcategory': 'psychologist_tips'})
        self.assertEqual(response.status_code, 200)
