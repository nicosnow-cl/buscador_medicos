from django import template
# import locale
register = template.Library()

@register.filter
def chileanCurrency(money_value):
    # locale.setlocale(locale.LC_MONETARY, 'es_CL.UTF-8')
    # return locale.currency(int(money_value), grouping=True)
    return '${:20,d}'.format(int(money_value)).replace(',', '.')
