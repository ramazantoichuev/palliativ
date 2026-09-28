from django import template
from django.utils.html import escape, linebreaks
from django.utils.safestring import mark_safe

from ..models.editable_text_block import EditableTextBlock

register = template.Library()


@register.simple_tag
def get_text_block(slug, fallback="", as_list=False):
    try:
        text = EditableTextBlock.objects.get(slug=slug).content
        from_db = True
    except EditableTextBlock.DoesNotExist:
        text = fallback
        from_db = False

    if not text:
        return ""
    if as_list:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        items = "".join(f"<li>{escape(line)}</li>" for line in lines)
        return mark_safe(f"<ul>{items}</ul>")
    if from_db:
        # Контент вводится в админке — экранируем, иначе stored XSS.
        return mark_safe(linebreaks(text, autoescape=True))
    # Fallback задаётся разработчиком в шаблоне и может содержать разметку.
    return mark_safe(linebreaks(text))
