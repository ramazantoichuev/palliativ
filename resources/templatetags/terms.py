# resources/templatetags/terms.py (новый файл)
from django import template

register = template.Library()

@register.inclusion_tag('partial/terms_popover_list.html')
def render_terms(resource):
    return {'terms': resource.terms.all()}