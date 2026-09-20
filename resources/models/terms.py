from django.db import models
from django.utils.translation import gettext_lazy as _


class Term(models.Model):
    name = models.CharField(_('Термин'), max_length=255, unique=True)
    definition = models.TextField(_('Определение'))

    class Meta:
        verbose_name = _('Медицинский термин')
        verbose_name_plural = _('Медицинские термины')

    def __str__(self):
        return self.name