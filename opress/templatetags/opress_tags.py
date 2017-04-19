from django import template
from opress.models import DIAS_SEMANA, MESES_ANYO

register = template.Library()

@register.filter
def mes(value):
    return MESES_ANYO[value.month - 1]

@register.filter
def dia_semana(value):
    return DIAS_SEMANA[value.weekday()]

@register.filter
def comillas(value):
    return value.replace('"', "'")
