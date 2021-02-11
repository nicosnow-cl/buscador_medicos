from django import template
register = template.Library()

@register.filter
def googleSearch(name):
    return name.replace(',', '').replace(' ', '+').lower()

@register.filter
def doctoraliaFilter(name):
    second_names, first_names = name.split(',')
    ordered_name = first_names + ' ' + second_names
    return ordered_name[1:].replace(' ', '%20').upper()