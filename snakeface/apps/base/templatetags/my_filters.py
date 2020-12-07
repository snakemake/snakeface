from django import template

register = template.Library()


@register.filter(name="replace", is_safe=True)
def replace(string, original, value):
    return string.replace(original, value)


@register.filter
def lookup(d, key):
    return d[key]


@register.filter
def range(min=5):
    return range(min)


@register.filter
def index(indexable, i):
    return indexable[i]
