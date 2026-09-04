import logging

from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

class BaseUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        MODERATOR = 'moderator', _('Модератор')
        MANAGER = 'manager', _('Менеджер')
        DOCTOR = 'doctor', _('Врач')
        PATIENT = 'patient', _('Пациент')

    ROLE_GROUPS = {
        Role.MANAGER: 'Managers',
        Role.MODERATOR: 'Moderators',
    }
    role = models.CharField(_('Роль'), max_length=20, choices=Role.choices, default=Role.PATIENT)
    is_approved = models.BooleanField(_('Одобрен'),default=False )
    first_name = models.CharField(_("Имя"), max_length=150, blank=False, null=False)
    last_name = models.CharField(_("Фамилия"), max_length=150, blank=False, null=False
    )
    email = models.EmailField(_("Email"),blank=False,null=False, unique=True )
    phone_regex = RegexValidator(regex=r'^\+996\d{9}$',
        message=_("Номер телефона должен быть в формате: '+996XXXXXXXXX' (всего 12 цифр)."))
    phone = models.CharField(_('Номер телефона'),
        validators=[phone_regex], max_length=13,unique=True,blank=False,null=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if self.role == self.Role.PATIENT:
            self.is_approved = True
        if self.role in [self.Role.ADMIN, self.Role.MANAGER, self.Role.MODERATOR]:
            self.is_staff = True
            self.is_approved = True
            if self.role == self.Role.ADMIN:
                self.is_superuser = True

        super().save(*args, **kwargs)

        if is_new:
            if self.role == self.Role.DOCTOR:
                DoctorProfile.objects.create(user=self)
            elif self.role == self.Role.PATIENT:
                PatientProfile.objects.create(user=self)

        group_name = self.ROLE_GROUPS.get(self.role)
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                self.groups.add(group)
            except Group.DoesNotExist:
                logger.warning(
                    "Группа '%s' не найдена — запустите setup_%s_group для роли %s",
                    group_name, self.role, self.role,
                )


class DoctorProfile(models.Model):
    user = models.OneToOneField(BaseUser,on_delete=models.CASCADE, related_name='doctor_profile')
    education = models.CharField(
        _('Образование или место учебы'),max_length=255, blank=True)
    skills = models.TextField(_('Навыки'),blank=True)

    def __str__(self):
        return self.user.get_full_name()


class PatientProfile(models.Model):
    user = models.OneToOneField( BaseUser, on_delete=models.CASCADE, related_name='patient_profile')
    diagnosis = models.TextField(_('Диагноз'),blank=True)

    def __str__(self):
        return self.user.get_full_name()
