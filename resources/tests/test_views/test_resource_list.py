from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from resources.constants import RESOURCES_PER_PAGE
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
        ResourceFactory(title='Тестовый материал')
        response = self.client.get(self.url)
        self.assertContains(response, 'Тестовый материал')

    def test_filter_by_audience(self):
        ResourceFactory(audience=Resource.AUDIENCE_SPECIALIST, title='Для специалиста')
        ResourceFactory(audience=Resource.AUDIENCE_CAREGIVER, title='Для ухаживающего')

        response = self.client.get(self.url, {'audience': Resource.AUDIENCE_SPECIALIST})

        self.assertContains(response, 'Для специалиста')
        self.assertNotContains(response, 'Для ухаживающего')

    def test_filter_by_subcategory(self):
        ResourceFactory(subcategory='npa', title='НПА материал')
        ResourceFactory(subcategory='care_feeding', title='Уход материал')

        response = self.client.get(self.url, {'subcategory': 'npa'})

        self.assertContains(response, 'НПА материал')
        self.assertNotContains(response, 'Уход материал')

    def test_filter_by_symptom(self):
        ResourceFactory(title='С болью', symptoms=[self.symptom_pain])
        ResourceFactory(title='С жаром', symptoms=[self.symptom_fever])

        response = self.client.get(self.url, {'symptom': self.symptom_pain.id})

        self.assertContains(response, 'С болью')
        self.assertNotContains(response, 'С жаром')

    def test_combined_filters(self):
        ResourceFactory(
            audience=Resource.AUDIENCE_SPECIALIST,
            subcategory='symptom_control',
            symptoms=[self.symptom_pain],
            title='Подходящий'
        )
        ResourceFactory(
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

    def test_filter_by_audience_and_pain_management_subcategory(self):
        ResourceFactory(
            audience=Resource.AUDIENCE_CAREGIVER,
            subcategory='pain_management',
            title='Про управление болью',
        )
        ResourceFactory(
            audience=Resource.AUDIENCE_CAREGIVER,
            subcategory='meds_rights',
            title='Про лекарства',
        )

        response = self.client.get(self.url, {
            'audience': Resource.AUDIENCE_CAREGIVER,
            'subcategory': 'pain_management',
        })

        self.assertContains(response, 'Про управление болью')
        self.assertNotContains(response, 'Про лекарства')

    def test_pain_management_empty_result_does_not_break_page(self):
        response = self.client.get(self.url, {'subcategory': 'pain_management'})
        self.assertEqual(response.status_code, 200)

    def test_pagination_links_keep_filters(self):
        for _ in range(RESOURCES_PER_PAGE + 1):
            ResourceFactory(audience="caregiver", subcategory="pain_management")
        response = self.client.get(
            self.url, {"audience": "caregiver", "subcategory": "pain_management"}
        )
        self.assertContains(response, "page=2")
        self.assertContains(response, "audience=caregiver")
        self.assertContains(response, "subcategory=pain_management")

    def test_chip_links_keep_other_filters_and_reset_page(self):
        ResourceFactory(audience="caregiver")
        response = self.client.get(
            self.url, {"audience": "caregiver", "symptom": self.symptom_pain.pk}
        )
        content = response.content.decode()
        chips = [
            line for line in content.splitlines()
            if "subcategory=pain_management" in line
        ]
        self.assertTrue(chips)
        self.assertIn("audience=caregiver", chips[0])
        self.assertIn(f"symptom={self.symptom_pain.pk}", chips[0])
        self.assertNotIn("page=", chips[0])


class ResourceListLocalizationTest(TestCase):
    """Интерфейс списка ресурсов на KY/EN: подписи и счётчик «Ещё N»."""

    def setUp(self):
        self.url = reverse('resources:resource_list')
        # LocaleMiddleware активирует язык на поток и не сбрасывает его —
        # возвращаем русский, чтобы не портить соседние тесты.
        self.addCleanup(translation.activate, "ru")

    def _get(self, lang):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = lang
        return self.client.get(self.url, HTTP_ACCEPT_LANGUAGE=lang)

    def test_audience_label_translated(self):
        for lang, label in (('ky', 'Аудитория'), ('en', 'Audience')):
            with self.subTest(lang=lang):
                response = self._get(lang)
                self.assertContains(response, f'>{label}</div>')
        self.assertNotContains(self._get('en'), '>Аудитория<')

    def test_more_counter_translated(self):
        for lang, template in (('ky', 'Дагы {}'), ('en', '{} more')):
            with self.subTest(lang=lang):
                response = self._get(lang)
                hidden = len(response.context['subcategory_hidden'])
                self.assertGreater(hidden, 0)
                self.assertContains(response, template.format(hidden))
                self.assertNotContains(response, f'Ещё {hidden}')
