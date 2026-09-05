from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from accounts.models import BaseUser


class Command(BaseCommand):
    help = 'Создаёт группу Moderators с правами на news и events'

    def handle(self, *args, **options):
        group_name = BaseUser.ROLE_GROUPS[BaseUser.Role.MODERATOR]
        group, created = Group.objects.get_or_create(name=group_name)

        app_models = {
            'news': ['post', 'category'],
            'events': ['event', 'eventregistration'],
        }

        permissions = []
        for app_label, model_names in app_models.items():
            for model_name in model_names:
                for action in ['add', 'change', 'view']:
                    codename = f'{action}_{model_name}'
                    try:
                        perm = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label
                        )
                        permissions.append(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'Permission {codename} для {app_label} не найден'
                        ))

        group.permissions.set(permissions)

        if created:
            self.stdout.write(self.style.SUCCESS('Группа Moderators создана'))
        else:
            self.stdout.write(self.style.SUCCESS('Группа Moderators обновлена'))