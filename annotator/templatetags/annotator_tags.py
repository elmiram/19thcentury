from django import template
from django.template import resolve_variable
from django.contrib.auth.models import Group

register = template.Library()
def multiply(value, arg):
    s = value*arg + 1 - 10
    return s

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

register.filter('multiply', multiply)