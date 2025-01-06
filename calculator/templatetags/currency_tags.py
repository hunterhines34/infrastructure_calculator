from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def currency(value):
    """Format value as USD currency"""
    if value is None:
        return "$0.00"
    try:
        value = Decimal(value)
        return f"${value:,.2f}"
    except (ValueError, TypeError, InvalidOperation):
        return "$0.00" 