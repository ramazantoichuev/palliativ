"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/6.1/topics/http/urls/

Examples:
Function views
1. Add an import:  from my_app import views
2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
1. Import the include() function: from django.urls import include, path
2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from events.sitemaps import EventSitemap
from news.sitemaps import PostSitemap
from resources.sitemaps import ResourceSitemap

sitemaps = {
    "news": PostSitemap,
    "events": EventSitemap,
    "resources": ResourceSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("main.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("events/", include("events.urls")),
    path("news/", include("news.urls")),
    path("patients/", include("patients.urls")),
    path("resources/", include("resources.urls")),
    path("faq/", include("faq.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
]