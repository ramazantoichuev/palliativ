from django.test import TestCase

from events.forms import EventAdminForm


class TestEventAdminForm(TestCase):
    """Форма админки с раздельными полями даты и времени (SplitDateTimeWidget)."""

    valid_data = {
        "title": "Школа паллиативной помощи",
        "slug": "school-admin-form",
        "description": "Описание",
        "content": "Содержание",
        "location": "г. Бишкек",
        "event_date_0": "2026-10-01",
        "event_date_1": "14:30",
    }

    def test_valid_split_datetime_is_accepted(self):
        form = EventAdminForm(data=self.valid_data)

        self.assertTrue(form.is_valid(), form.errors)
        cleaned = form.cleaned_data["event_date"]
        self.assertEqual(
            (cleaned.year, cleaned.month, cleaned.day, cleaned.hour, cleaned.minute),
            (2026, 10, 1, 14, 30),
        )

    def test_missing_date_or_time_is_rejected(self):
        for field in ("event_date_0", "event_date_1"):
            data = {**self.valid_data, field: ""}

            form = EventAdminForm(data=data)

            self.assertFalse(form.is_valid())
            self.assertIn("event_date", form.errors)

    def test_widget_renders_native_date_and_time_inputs(self):
        html = str(EventAdminForm()["event_date"])

        self.assertIn('type="date"', html)
        self.assertIn('type="time"', html)
