from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from transliterate import translit


class Event(models.Model):
    title = models.CharField(_("Заголовок"), max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(_("Описание"))
    content = models.TextField(_("Текст"))
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Мероприятие")
        verbose_name_plural = _("Мероприятия")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            latin_title = translit(self.title, 'ru', reversed=True)
            base_slug = slugify(latin_title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:event_detail", kwargs={"slug": self.slug})

    @property
    def is_past(self):
        return self.event_date < timezone.now()


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    full_name = models.CharField(_("ФИО"), max_length=255)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Телефон"), max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(_("Рассмотрено"), default=False)

    class Meta:
        verbose_name = _("Регистрация на мероприятие")
        verbose_name_plural = _("Регистрации на мероприятия")

    def __str__(self):
        return f"{self.full_name} — {self.event.title}"
