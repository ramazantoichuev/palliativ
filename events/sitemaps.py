from django.contrib.sitemaps import Sitemap

from .models import Event


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Event.objects.all()
