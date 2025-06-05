from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter(name='divide')
def divide(value, arg):
    """Divides the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def get(dictionary, key):
    """
    Gets a value from a dictionary using a variable as key
    Example usage: {{ dict|get:key_var }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
