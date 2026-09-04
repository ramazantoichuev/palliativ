from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def canonical_url(context):
    request = context.get('request')
    if not request:
        return ""
    return request.build_absolute_uri(request.path)
