from django.contrib.sitemaps import Sitemap
from .models.resources import Resource


class ResourceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Resource.objects.all()

    def lastmod(self, obj):
        return obj.updated_at