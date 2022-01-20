from django import template

register = template.Library()

@register.filter
def sec_to_hh_mm(secunds):
    sec_value = secunds % (24 * 3600)
    hour_value = sec_value // 3600
    sec_value %= 3600
    min = sec_value // 60
    
    return f'{hour_value:02d}:{min:02d}'