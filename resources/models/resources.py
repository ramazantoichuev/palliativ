from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.validators import validate_resource_file_size


class Resource(models.Model):
    AUDIENCE_SPECIALIST = 'specialist'
    AUDIENCE_CAREGIVER = 'caregiver'

    AUDIENCE_CHOICES = [
        (AUDIENCE_SPECIALIST, _('Руководство для специалистов')),
        (AUDIENCE_CAREGIVER, _('Советы ухаживающим')),
    ]

    SUBCATEGORY_CHOICES = [
        ('symptom_control', _('Контроль симптомов')),
        ('end_of_life_care', _('Уход в конце жизни')),
        ('npa', _('НПА (Нормативно-правовые акты)')),

        ('care_feeding', _('Уход и кормление')),
        ('psychologist_tips', _('Советы психолога')),
        ('meds_rights', _('Лекарства и права пациента')),
        ('social_support', _('Соцподдержка')),
    ]

    title = models.CharField(_('Заголовок'), max_length=255)
    description = models.TextField(_('Описание'), blank=True, max_length=settings.DESCRIPTION_MAX_LENGTH)

    audience = models.CharField(
        _('Целевая аудитория'),
        max_length=20,
        choices=AUDIENCE_CHOICES
    )
    subcategory = models.CharField(
        _('Подкатегория'),
        max_length=30,
        choices=SUBCATEGORY_CHOICES
    )
    symptoms = models.ManyToManyField('patients.Symptom',
        verbose_name=_('Симптомы'),
        blank=True,
        related_name='resources'
    )

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Справочный материал')
        verbose_name_plural = _('Справочные материалы')

    def __str__(self):
        return self.title


class ResourceFile(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Ресурс')
    )
    file = models.FileField(
        _('Файл'),
        upload_to='resources/files/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'pdf', 'doc', 'docx']),
            validate_resource_file_size,
    ],
    )
    class Meta:
        verbose_name = _('Файл ресурса')
        verbose_name_plural = _('Файлы ресурса')

    def __str__(self):
        return self.file.name


class ResourceVideoLink(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name=_('Ресурс')
    )
    url = models.URLField(_('Ссылка на YouTube'))
    class Meta:
        verbose_name = _('Видео-ссылка')
        verbose_name_plural = _('Видео-ссылки')

    def __str__(self):
        return self.url
