from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import TestCase


class SetupManagersGroupCommandTest(TestCase):
    def test_setup_managers_group_creation_and_permissions(self):
        call_command('setup_manager_group')
        group = Group.objects.get(name='Managers')
        expected_permissions = {
            'main': {
                'consultationrequest': ['view', 'change'],
            },
            'patients': {
                'patientcard': ['add', 'change', 'view'],
                'symptom': ['view'],
            },
            'accounts': {
                'patientprofile': ['view', 'change'],
                'doctorprofile': ['view'],
                'baseuser': ['view'],
            },
            'events': {
                'eventregistration': ['view', 'change'],
            }
        }
        for app_label, models in expected_permissions.items():
            for model_name, actions in models.items():
                for action in actions:
                    codename = f"{action}_{model_name}"
                    try:
                        perm = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label
                        )
                        self.assertIn(
                            perm,
                            group.permissions.all(),
                            f"Право '{codename}' для '{app_label}' должно быть назначено группе Managers."
                        )
                    except Permission.DoesNotExist:
                        pass

    def test_setup_managers_group_idempotency(self):
        call_command('setup_manager_group')
        call_command('setup_manager_group')
        self.assertEqual(Group.objects.filter(name='Managers').count(), 1)