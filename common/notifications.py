import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_admins(subject, message):
    if not settings.NOTIFICATION_EMAILS:
        return
    try:
        send_mail(
            subject=f'[Паллиатив.kg] {subject}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.NOTIFICATION_EMAILS,
            fail_silently=False,
        )
    except Exception:
        logger.error('Не удалось отправить уведомление администраторам: %s', subject, exc_info=True)


def send_confirmation(to_email, subject, message):
    if not to_email:
        return
    try:
        send_mail(
            subject=f'[Паллиатив.kg] {subject}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception:
        logger.error('Не удалось отправить подтверждение на %s', to_email, exc_info=True)