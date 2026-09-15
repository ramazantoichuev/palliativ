from django.db import models
from django.utils.translation import gettext_lazy as _


class FAQItem(models.Model):
    question = models.CharField(_('Вопрос'), max_length=500)
    answer = models.TextField(_('Ответ'))
    is_active = models.BooleanField(_('Активен'), default=True)
    order = models.PositiveIntegerField(_('Порядок отображения'), default=0)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('Вопрос FAQ')
        verbose_name_plural = _('Вопросы FAQ')
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question
