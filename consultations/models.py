from django.db import models
from django.utils.translation import gettext_lazy as _

class ConsultationRequest(models.Model):
    TOPIC_CHOICES = [
        ('medical_help', _('Медицинская помощь')),
        ('cooperation', _('Сотрудничество')),
        ('partnership', _('Партнерство')),
    ]

    first_name = models.CharField(_('Имя'), max_length=255)
    phone = models.CharField(_('Телефон'), max_length=20)
    email = models.EmailField(_('Email'))
    topic = models.CharField(_('Тема обращения'), max_length=20, choices=TOPIC_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} — {self.get_topic_display()}"

# Create your models here.
