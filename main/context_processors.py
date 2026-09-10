from django.conf import settings


def analytics(request):
    """ID счётчиков аналитики для partial/analytics.html (пустые — скрипты не рендерятся)."""
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'YANDEX_METRIKA_ID': settings.YANDEX_METRIKA_ID,
    }
