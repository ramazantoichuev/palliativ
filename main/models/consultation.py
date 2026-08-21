from django.db import models
from django.utils.translation import gettext_lazy as _


class ConsultationRequest(models.Model):
    TOPIC_CHOICES = [
        ('medical_help', _('Медицинская помощь')),
        ('cooperation', _('Сотрудничество')),
        ('partnership', _('Партнерство')),
    ]
    STATUS_CHOICES = [
        ('new', _('Новая')),
        ('in_progress', _('В работе')),
        ('closed', _('Рассмотрена')),
        ('rejected', _('Отклонена')),
    ]

    first_name = models.CharField(_('Имя'), max_length=255)
    phone = models.CharField(_('Телефон'), max_length=20)
    email = models.EmailField(_('Email'))
    topic = models.CharField(_('Тема обращения'), max_length=20, choices=TOPIC_CHOICES)

    status = models.CharField(
        _('Статус заявки'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} — {self.get_topic_display()} [{self.get_status_display()}]"
