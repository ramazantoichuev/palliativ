from django.conf import settings


def analytics(request):
    """ID счётчиков аналитики для partial/analytics.html (пустые — скрипты не рендерятся)."""
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
        'YANDEX_METRIKA_ID': settings.YANDEX_METRIKA_ID,
    }


def turnstile_keys(request):
    #Глобально добавляет публичный ключ Cloudflare Turnstile во все шаблоны.
    return {
        'TURNSTILE_SITE_KEY': settings.TURNSTILE_SITE_KEY
    }


def site_contacts(request):
    """Контакты Ассоциации для футера (base.html) и страницы «Контакты»."""
    from .models.site_contacts import SiteContacts

    return {"site_contacts": SiteContacts.load()}
