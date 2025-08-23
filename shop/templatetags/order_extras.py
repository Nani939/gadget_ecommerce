from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_days(value, days):
    """Adds days to a datetime/date object."""
    if not value:
        return None
    try:
        return value + timedelta(days=int(days))
    except Exception:
        return value
