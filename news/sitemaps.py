from django.contrib.sitemaps import Sitemap

from .models.posts import Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.created_at
