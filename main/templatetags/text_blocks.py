from django import template
from django.utils.html import escape, linebreaks
from django.utils.safestring import mark_safe

from ..models.editable_text_block import EditableTextBlock

register = template.Library()


@register.simple_tag
def get_text_block(slug, fallback="", as_list=False):
    try:
        obj = EditableTextBlock.objects.get(slug=slug)
        text = obj.content
    except EditableTextBlock.DoesNotExist:
        text = fallback

    if not text:
        return ""
    if as_list:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        html_list = "<ul>"
        for line in lines:
            html_list += f"<li>{escape(line)}</li>"
        html_list += "</ul>"
        return mark_safe(html_list)
    return mark_safe(linebreaks(text))
