from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Split a string by delimiter"""
    return value.split(delimiter)

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary"""
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0