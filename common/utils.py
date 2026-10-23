def get_client_ip(request):
    """IP клиента: X-Real-IP (его выставляет nginx), иначе REMOTE_ADDR.

    X-Forwarded-For не используем: клиент может подставить его сам.
    """
    real_ip = request.META.get("HTTP_X_REAL_IP", "").strip()
    return real_ip or request.META.get("REMOTE_ADDR", "")