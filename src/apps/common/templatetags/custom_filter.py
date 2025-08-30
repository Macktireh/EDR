from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(value, index):
    return value[index]

@register.simple_tag
def lookup2(items, index):
    if index < 0 or index >= len(items):
        return ''
    return items[index]