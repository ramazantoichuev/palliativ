from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models.consultation import ConsultationRequest
from main.tests.factories import (
    ConsultationRequestFactory,  # поправьте путь, если factories.py лежит в другом месте
)

User = get_user_model()

HOST = {"SERVER_NAME": "127.0.0.1"}


def make_request(first_name, status="new", age_minutes=0, **extra):
    """created_at задаётся auto_now_add, поэтому сдвигаем его отдельным update()."""
    obj = ConsultationRequestFactory(first_name=first_name, status=status, **extra)
    ConsultationRequest.objects.filter(pk=obj.pk).update(
        created_at=timezone.now() - timedelta(minutes=age_minutes)
    )
    return obj


def listed_names(response):
    return [obj.first_name for obj in response.context["cl"].result_list]


class ConsultationAdminTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_superuser(
            username="admin_consult", email="admin_consult@test.kg", password="AdminPass123"
        )
        self.client.force_login(self.admin_user)
        self.changelist_url = reverse("admin:main_consultationrequest_changelist")

    def get_list(self, params=None):
        return self.client.get(self.changelist_url, params or {}, **HOST)

    def run_action(self, action, objs):
        return self.client.post(
            self.changelist_url,
            data={"action": action, "_selected_action": [o.pk for o in objs]},
            follow=True,
            **HOST,
        )

    def refreshed_status(self, obj):
        return ConsultationRequest.objects.get(pk=obj.pk).status


class ConsultationAdminStatusFilterTests(ConsultationAdminTestCase):
    def setUp(self):
        super().setUp()
        self.new = make_request("Новая-1", "new", age_minutes=10)
        self.in_progress = make_request("Работа-1", "in_progress", age_minutes=20)
        self.closed = make_request("Рассмотрена-1", "closed", age_minutes=30)
        self.rejected = make_request("Отклонена-1", "rejected", age_minutes=40)

    def test_default_list_shows_only_active_requests(self):
        response = self.get_list()

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(listed_names(response), ["Новая-1", "Работа-1"])

    def test_all_parameter_shows_every_request(self):
        response = self.get_list({"status_group": "all"})

        self.assertCountEqual(
            listed_names(response),
            ["Новая-1", "Работа-1", "Рассмотрена-1", "Отклонена-1"],
        )

    def test_explicit_active_parameter_matches_default(self):
        response = self.get_list({"status_group": "active"})

        self.assertCountEqual(listed_names(response), ["Новая-1", "Работа-1"])

    def test_each_status_option_shows_only_that_status(self):
        expected = {
            "new": ["Новая-1"],
            "in_progress": ["Работа-1"],
            "closed": ["Рассмотрена-1"],
            "rejected": ["Отклонена-1"],
        }
        for value, names in expected.items():
            with self.subTest(status_group=value):
                response = self.get_list({"status_group": value})
                self.assertEqual(listed_names(response), names)

    def test_filter_offers_all_option(self):
        response = self.get_list()
        cl = response.context["cl"]

        choices = list(cl.filter_specs[0].choices(cl))
        by_display = {str(c["display"]): c for c in choices}

        self.assertIn("Все", by_display)
        self.assertIn("status_group=all", by_display["Все"]["query_string"])
        self.assertFalse(by_display["Все"]["selected"])
        self.assertTrue(by_display["Активные"]["selected"])

    def test_status_filter_combines_with_topic_filter(self):
        make_request("Сотрудничество-1", "new", topic="cooperation")

        response = self.get_list({"topic__exact": "cooperation"})

        self.assertEqual(listed_names(response), ["Сотрудничество-1"])

    def test_status_filter_does_not_leak_processed_when_topic_selected(self):
        make_request("Закрытая-сотр", "closed", topic="cooperation")

        response = self.get_list({"topic__exact": "cooperation"})

        self.assertEqual(listed_names(response), [])

    def test_search_works_together_with_all_filter(self):
        make_request(
            "Поиск-закрытая", "closed", email="unique.search@example.com", phone="+996700999888"
        )

        by_email = self.get_list({"status_group": "all", "q": "unique.search"})
        by_phone = self.get_list({"status_group": "all", "q": "996700999888"})
        by_name = self.get_list({"status_group": "all", "q": "Поиск-закр"})

        self.assertEqual(listed_names(by_email), ["Поиск-закрытая"])
        self.assertEqual(listed_names(by_phone), ["Поиск-закрытая"])
        self.assertEqual(listed_names(by_name), ["Поиск-закрытая"])


class ConsultationAdminOrderingTests(ConsultationAdminTestCase):
    def test_new_above_in_progress_and_processed_below_in_all_mode(self):
        # создаём вперемешку, чтобы порядок не совпал со случайным порядком вставки
        make_request("Закрытая", "closed", age_minutes=1)  # самая свежая, но обработанная
        make_request("В работе", "in_progress", age_minutes=2)
        make_request("Отклонённая", "rejected", age_minutes=3)
        make_request("Новая", "new", age_minutes=60)  # самая старая, но новая

        response = self.get_list({"status_group": "all"})

        self.assertEqual(
            listed_names(response),
            ["Новая", "В работе", "Закрытая", "Отклонённая"],
        )

    def test_within_group_newer_requests_come_first(self):
        make_request("Новая-старая", "new", age_minutes=30)
        make_request("Новая-свежая", "new", age_minutes=5)
        make_request("Работа-старая", "in_progress", age_minutes=40)
        make_request("Работа-свежая", "in_progress", age_minutes=15)

        response = self.get_list()

        self.assertEqual(
            listed_names(response),
            ["Новая-свежая", "Новая-старая", "Работа-свежая", "Работа-старая"],
        )

    def test_column_header_sorting_overrides_default_order(self):
        make_request("Борис", "new", age_minutes=1)
        make_request("Анна", "in_progress", age_minutes=2)

        default_order = listed_names(self.get_list())
        # o=1 — сортировка по первой колонке list_display (first_name)
        sorted_by_name = listed_names(self.get_list({"o": "1"}))

        self.assertEqual(default_order, ["Борис", "Анна"])
        self.assertEqual(sorted_by_name, ["Анна", "Борис"])


class ConsultationAdminBulkActionTests(ConsultationAdminTestCase):
    def setUp(self):
        super().setUp()
        self.first = make_request("Выбранная-1", "new", age_minutes=1)
        self.second = make_request("Выбранная-2", "new", age_minutes=2)
        self.untouched = make_request("Невыбранная", "new", age_minutes=3)

    def assert_message(self, response, text):
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn(text, messages)

    def test_take_in_progress_changes_only_selected(self):
        response = self.run_action("mark_in_progress", [self.first, self.second])

        self.assertEqual(self.refreshed_status(self.first), "in_progress")
        self.assertEqual(self.refreshed_status(self.second), "in_progress")
        self.assertEqual(self.refreshed_status(self.untouched), "new")
        self.assert_message(response, "Обновлено заявок: 2")

    def test_mark_closed_changes_only_selected(self):
        response = self.run_action("mark_closed", [self.first, self.second])

        self.assertEqual(self.refreshed_status(self.first), "closed")
        self.assertEqual(self.refreshed_status(self.second), "closed")
        self.assertEqual(self.refreshed_status(self.untouched), "new")
        self.assert_message(response, "Обновлено заявок: 2")

    def test_reject_changes_only_selected(self):
        response = self.run_action("mark_rejected", [self.first])

        self.assertEqual(self.refreshed_status(self.first), "rejected")
        self.assertEqual(self.refreshed_status(self.second), "new")
        self.assertEqual(self.refreshed_status(self.untouched), "new")
        self.assert_message(response, "Обновлено заявок: 1")

    def test_action_does_not_modify_other_fields_of_any_request(self):
        before = list(
            ConsultationRequest.objects.order_by("pk").values(
                "pk", "first_name", "phone", "email", "topic", "created_at"
            )
        )

        self.run_action("mark_closed", [self.first, self.second])

        after = list(
            ConsultationRequest.objects.order_by("pk").values(
                "pk", "first_name", "phone", "email", "topic", "created_at"
            )
        )
        self.assertEqual(before, after)

    def test_processed_requests_leave_default_list_after_action(self):
        self.run_action("mark_closed", [self.first, self.second])

        response = self.get_list()

        self.assertEqual(listed_names(response), ["Невыбранная"])


class ConsultationAdminStatusChangeTests(ConsultationAdminTestCase):
    def test_list_editable_status_change_removes_request_from_active(self):
        obj = make_request("Через-список", "new")

        response = self.client.post(
            self.changelist_url,
            data={
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": obj.pk,
                "form-0-status": "closed",
                "_save": "Save",
            },
            **HOST,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.refreshed_status(obj), "closed")
        self.assertEqual(listed_names(self.get_list()), [])
        self.assertEqual(
            listed_names(self.get_list({"status_group": "closed"})), ["Через-список"]
        )

    def test_change_form_save_removes_request_from_active(self):
        obj = make_request("Через-карточку", "in_progress")

        response = self.client.post(
            reverse("admin:main_consultationrequest_change", args=[obj.pk]),
            data={
                "first_name": obj.first_name,
                "phone": obj.phone,
                "email": obj.email,
                "topic": obj.topic,
                "status": "rejected",
                "_save": "Save",
            },
            **HOST,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.refreshed_status(obj), "rejected")
        self.assertEqual(listed_names(self.get_list()), [])

    def test_change_page_still_renders(self):
        obj = make_request("Карточка", "new")

        response = self.client.get(
            reverse("admin:main_consultationrequest_change", args=[obj.pk]), **HOST
        )

        self.assertEqual(response.status_code, 200)
