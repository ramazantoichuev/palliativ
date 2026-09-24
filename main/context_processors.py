from django.conf import settings


def analytics(request):
    """ID счётчиков аналитики для partial/analytics.html (пустые — скрипты не рендерятся)."""
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
        'YANDEX_METRIKA_ID': settings.YANDEX_METRIKA_ID,
    }
