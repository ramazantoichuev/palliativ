from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemSettings(models.Model):
    patient_registration_enabled = models.BooleanField(
        _("Регистрация пациентов включена"), default=True
    )
    doctor_registration_enabled = models.BooleanField(
        _("Регистрация врачей включена"), default=True
    )

    class Meta:
        verbose_name = _("Системные настройки")
        verbose_name_plural = _("Системные настройки")

    def __str__(self):
        return str(_("Системные настройки"))

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj