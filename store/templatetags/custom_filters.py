# store/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='divisibleby')
def divisibleby(value, num):
    """
    Returns a list of lists, where each inner list contains `num` items from `value`.
    """
    return [value[i:i + num] for i in range(0, len(value), num)]