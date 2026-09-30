from django.test import TestCase

from main.models.system_settings import SystemSettings


class SystemSettingsModelTests(TestCase):
    def test_load_creates_settings_with_defaults_if_none_exist(self):
        self.assertEqual(SystemSettings.objects.count(), 0)

        settings_obj = SystemSettings.load()

        self.assertEqual(SystemSettings.objects.count(), 1)
        self.assertTrue(settings_obj.patient_registration_enabled)
        self.assertTrue(settings_obj.doctor_registration_enabled)

    def test_load_returns_existing_settings_without_creating_duplicate(self):
        SystemSettings.load()

        settings_obj = SystemSettings.load()

        self.assertEqual(SystemSettings.objects.count(), 1)
        self.assertEqual(settings_obj.pk, 1)

    def test_creating_second_instance_does_not_create_second_row(self):
        first = SystemSettings.objects.create(patient_registration_enabled=True)

        second = SystemSettings(patient_registration_enabled=False)
        second.save()

        self.assertEqual(SystemSettings.objects.count(), 1)
        self.assertEqual(first.pk, second.pk)

    def test_saving_overwrites_the_single_existing_record(self):
        settings_obj = SystemSettings.load()
        settings_obj.patient_registration_enabled = False
        settings_obj.save()

        reloaded = SystemSettings.objects.get(pk=1)

        self.assertEqual(SystemSettings.objects.count(), 1)
        self.assertFalse(reloaded.patient_registration_enabled)