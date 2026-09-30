from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteContacts(models.Model):
    """Контакты Ассоциации. Синглтон: save() форсирует pk=1."""

    phone = models.CharField(
        _("Телефон для tel:-ссылки"),
        max_length=20,
        help_text=_("В формате +996312214015"),
    )
    phone_display = models.CharField(
        _("Телефон (отображаемый текст)"), max_length=30
    )
    email = models.EmailField(_("Email"))
    whatsapp_url = models.URLField(_("Ссылка WhatsApp"), blank=True)
    whatsapp_display = models.CharField(
        _("WhatsApp (отображаемый текст)"), max_length=30, blank=True
    )
    facebook_url = models.URLField(_("Ссылка Facebook"), blank=True)
    instagram_url = models.URLField(_("Ссылка Instagram"), blank=True)
    twogis_url = models.URLField(_("Ссылка на 2ГИС"), blank=True)
    address = models.CharField(_("Адрес"), max_length=255)

    class Meta:
        verbose_name = _("Контакты сайта")
        verbose_name_plural = _("Контакты сайта")

    def __str__(self):
        return str(_("Контакты сайта"))

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    @staticmethod
    def _url_handle(url):
        return url.rstrip("/").rsplit("/", 1)[-1] if url else ""

    @property
    def facebook_handle(self):
        return self._url_handle(self.facebook_url)

    @property
    def instagram_handle(self):
        return self._url_handle(self.instagram_url)
