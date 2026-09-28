from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event
from news.models.posts import Category, Post
from resources.models.resources import Resource


class SearchResultsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Новости")

        cls.post = Post.objects.create(
            title="Паллиативная помощь",
            description="Новости о развитии паллиативной помощи",
            content="Текст новости",
            category=cls.category,
        )

        cls.event = Event.objects.create(
            title="Семинар по паллиативной помощи",
            description="Обучающий семинар для специалистов",
            content="Программа мероприятия",
            event_date=timezone.now() + timedelta(days=1),
            location="Бишкек",
        )

        cls.resource = Resource.objects.create(
            title="Руководство по паллиативной помощи",
            description="Практические материалы для специалистов",
            audience=Resource.AUDIENCE_SPECIALIST,
            subcategory="symptom_control",
        )

    def test_search_finds_content(self):
        response = self.client.get(
            reverse("main:search"),
            {"q": "паллиатив"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.event.title)
        self.assertContains(response, self.resource.title)

    def test_search_finds_content_in_translation(self):
        self.post.title_en = "Palliative care news"
        self.post.description_en = "News about palliative care"
        self.post.save()

        self.event.title_ky = "Паллиативдик жардам боюнча семинар"
        self.event.description_ky = "Адистер үчүн окуу семинары"
        self.event.save()

        self.resource.title_en = "Palliative care guide"
        self.resource.description_en = "Practical materials for specialists"
        self.resource.save()

        response = self.client.get(
            reverse("main:search"),
            {"q": "Palliative"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context["news_results"])
        self.assertIn(self.resource, response.context["resource_results"])
        self.assertFalse(response.context["event_results"].exists())

        response = self.client.get(
            reverse("main:search"),
            {"q": "Паллиативдик"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.event, response.context["event_results"])
        self.assertFalse(response.context["news_results"].exists())
        self.assertFalse(response.context["resource_results"].exists())

    def test_search_returns_no_results(self):
        response = self.client.get(
            reverse("main:search"),
            {"q": "несуществующийзапрос"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "несуществующийзапрос")
        self.assertTrue(response.context["search_allowed"])

        self.assertFalse(response.context["news_results"].exists())
        self.assertFalse(response.context["event_results"].exists())
        self.assertFalse(response.context["resource_results"].exists())

    def test_search_empty_query(self):
        response = self.client.get(reverse("main:search"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "")
        self.assertFalse(response.context["search_allowed"])

        self.assertFalse(response.context["news_results"].exists())
        self.assertFalse(response.context["event_results"].exists())
        self.assertFalse(response.context["resource_results"].exists())

    def test_search_short_query(self):
        response = self.client.get(
            reverse("main:search"),
            {"q": "а"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "а")
        self.assertFalse(response.context["search_allowed"])

        self.assertFalse(response.context["news_results"].exists())
        self.assertFalse(response.context["event_results"].exists())
        self.assertFalse(response.context["resource_results"].exists())
