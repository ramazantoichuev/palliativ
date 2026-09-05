from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from accounts.models import BaseUser


class Command(BaseCommand):
    help = 'Настройка группы Managers и назначение ей достаточных прав по ТЗ.'

    def handle(self, *args, **options):
        group_name = BaseUser.ROLE_GROUPS[BaseUser.Role.MANAGER]
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(f"Создана новая группа: {group_name}")
        else:
            self.stdout.write(f"Настройка существующей группы: {group_name}")
        required_permissions = {
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

        permissions_to_set = []

        for app_label, models in required_permissions.items():
            for model_name, actions in models.items():
                for action in actions:
                    codename = f"{action}_{model_name}"
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label
                        )
                        permissions_to_set.append(permission)
                    except ObjectDoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Предупреждение: Permission '{codename}' для приложения '{app_label}' не найден в БД. Проверьте миграции."
                            )
                        )
        group.permissions.set(permissions_to_set)

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно синхронизировано прав для группы {group_name}: {len(permissions_to_set)}"
            )
        )
