from django.db import models
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    full_name = models.CharField(_('ФИО'), max_length=255)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Телефон'), max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.event.title}"

# Create your models here.
