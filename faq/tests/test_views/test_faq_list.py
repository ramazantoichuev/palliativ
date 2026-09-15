from django.test import TestCase
from django.urls import reverse

from faq.models import FAQItem


class TestFAQListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("faq:faq_list")
        cls.first = FAQItem.objects.create(
            question="Что такое паллиативная помощь?",
            answer="Комплексная поддержка пациентов и их семей.",
            order=1,
        )
        cls.second = FAQItem.objects.create(
            question="Как зарегистрироваться на мероприятие?",
            answer="Заполните форму на странице мероприятия.",
            order=2,
        )
        cls.hidden = FAQItem.objects.create(
            question="Скрытый вопрос",
            answer="Не должен отображаться.",
            is_active=False,
            order=3,
        )

    def test_page_opens_and_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "faq/faq_list.html")

    def test_shows_active_questions_and_answers(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Что такое паллиативная помощь?")
        self.assertContains(response, "Комплексная поддержка пациентов и их семей.")
        self.assertContains(response, "Как зарегистрироваться на мероприятие?")

    def test_inactive_question_is_hidden(self):
        response = self.client.get(self.url)

        self.assertNotContains(response, "Скрытый вопрос")
        self.assertNotIn(self.hidden, response.context["faq_items"])

    def test_questions_are_ordered_by_order_field(self):
        FAQItem.objects.filter(pk=self.first.pk).update(order=5)

        response = self.client.get(self.url)

        self.assertEqual(
            list(response.context["faq_items"]), [self.second, self.first]
        )

    def test_faq_link_is_present_in_navigation(self):
        response = self.client.get(self.url)

        self.assertContains(response, f'href="{self.url}"')

    def test_empty_state_is_shown_when_no_questions(self):
        FAQItem.objects.all().delete()

        response = self.client.get(self.url)

        self.assertContains(response, "Вопросы пока не добавлены.")

    def test_interface_strings_go_through_translation(self):
        """Заголовок страницы не должен утекать в вёрстку по-русски при другом языке."""
        response = self.client.get(self.url, headers={"accept-language": "en"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frequently Asked Questions")
        self.assertNotContains(response, "Часто задаваемые вопросы")
