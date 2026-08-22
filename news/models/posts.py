from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_('Название'), max_length=150, unique=True)

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(_('Заголовок'), max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField(_('Текст'))
    description = models.TextField(_('Описание'))
    image = models.ImageField(_('Картинка'), upload_to='news/', blank=True, null=True)
    category = models.ForeignKey(
        Category, verbose_name=_('Категория'),
        on_delete=models.PROTECT, related_name='posts')
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        ordering = ['-created_at']

    def __str__(self):
        return self.title
