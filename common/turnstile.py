import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_turnstile_token(token: str, remote_ip: str | None = None) -> bool:
    if not token:
        return False

    url = "https://cloudflare.com"
    payload = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip
    try:
        response = requests.post(url, data=payload, timeout=4.0)
        if response.status_code >= 500:
            logger.warning(f"Ошибка сервера Cloudflare Turnstile: {response.status_code}. Доступ разрешен (fail-open).")
            return True

        data = response.json()
        return bool(data.get("success", False))

    except requests.RequestException as e:
        logger.warning(f"Сбой подключения к Cloudflare Turnstile: {e}. Доступ разрешен (fail-open).")
        return True
