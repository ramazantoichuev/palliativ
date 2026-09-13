import re

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from transliterate import translit

from common.validators import validate_resource_file_size


class Resource(models.Model):
    AUDIENCE_SPECIALIST = "specialist"
    AUDIENCE_CAREGIVER = "caregiver"

    AUDIENCE_CHOICES = [
        (AUDIENCE_SPECIALIST, _("Руководство для специалистов")),
        (AUDIENCE_CAREGIVER, _("Советы ухаживающим")),
    ]

    SUBCATEGORY_CHOICES = [
        ("symptom_control", _("Контроль симптомов")),
        ("end_of_life_care", _("Уход в конце жизни")),
        ("npa", _("НПА (Нормативно-правовые акты)")),
        ("care_feeding", _("Уход и кормление")),
        ("psychologist_tips", _("Советы психолога")),
        ("meds_rights", _("Лекарства и права пациента")),
        ("social_support", _("Соцподдержка")),
    ]

    title = models.CharField(_("Заголовок"), max_length=255)
    description = models.TextField(
        _("Описание"), blank=True, max_length=settings.DESCRIPTION_MAX_LENGTH
    )
    slug = models.SlugField(_("Слаг"), unique=True)

    audience = models.CharField(
        _("Целевая аудитория"), max_length=20, choices=AUDIENCE_CHOICES
    )
    subcategory = models.CharField(
        _("Подкатегория"), max_length=30, choices=SUBCATEGORY_CHOICES
    )
    symptoms = models.ManyToManyField(
        "patients.Symptom",
        verbose_name=_("Симптомы"),
        blank=True,
        related_name="resources",
    )

    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)

    class Meta:
        verbose_name = _("Справочный материал")
        verbose_name_plural = _("Справочные материалы")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            latin_title = translit(self.title, "ru", reversed=True)
            base_slug = slugify(latin_title)
            slug = base_slug
            counter = 1
            while Resource.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("resources:resource_detail", kwargs={"slug": self.slug})


class ResourceFile(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name=_("Ресурс"),
    )
    file = models.FileField(
        _("Файл"),
        upload_to="resources/files/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp", "pdf", "doc", "docx"]
            ),
            validate_resource_file_size,
        ],
    )

    class Meta:
        verbose_name = _("Файл ресурса")
        verbose_name_plural = _("Файлы ресурса")

    def __str__(self):
        return self.file.name


class ResourceVideoLink(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name=_("Ресурс"),
    )

    url = models.URLField(_('Ссылка на YouTube'))

    def get_embed_url(self):
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/live\/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.url)
            if match:
                return f'https://www.youtube.com/embed/{match.group(1)}'
        return None

    class Meta:
        verbose_name = _("Видео-ссылка")
        verbose_name_plural = _("Видео-ссылки")

    def __str__(self):
        return self.url
