from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from common.utils import get_client_ip

RATE_LIMIT_MESSAGE = _("Слишком много попыток. Повторите позже")
def _key(name, ip):
    return f"ratelimit:{name}:{ip}"


def register_hit(name, ip, window):
    """Увеличивает счётчик. Окно отсчитывается от первой попытки."""
    key = _key(name, ip)
    cache.add(key, 0, window)
    try:
        return cache.incr(key)
    except ValueError:  # ключ истёк между add и incr
        cache.set(key, 1, window)
        return 1


def is_limited(name, ip, limit):
    """Достигнут ли лимит, не увеличивая счётчик (для входа)."""
    return cache.get(_key(name, ip), 0) >= limit


def allow_attempt(name, ip, limit, window):
    """Для форм: считает попытку. False, если это (limit+1)-я и дальше."""
    return register_hit(name, ip, window) <= limit

def check_rate_limit(request, name):
    """True, если попытка разрешена. Лимиты берутся из settings.RATE_LIMITS."""
    limit, window = settings.RATE_LIMITS[name]
    return allow_attempt(name, get_client_ip(request), limit, window)