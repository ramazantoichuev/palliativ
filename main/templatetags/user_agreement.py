from django import template

from ..user_agreement import is_user_agreement_published

register = template.Library()


@register.simple_tag
def user_agreement_published():
    """True, если пользовательское соглашение готово к показу (см. user_agreement.py)."""
    return is_user_agreement_published()
