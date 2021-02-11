def chileanCurrency(money_value):
    return '${:20,d}'.format(int(money_value)).replace(',', '.')

def toNormalName(name):
    second_names, first_names = name.split(',')
    return first_names + ' ' + second_names

def toGoogleSearch(name):
    return name.replace(',', '').replace(' ', '+').lower()

def toDoctoraliaSearch(name):
    second_names, first_names = name.split(',')
    ordered_name = first_names + ' ' + second_names
    return ordered_name[1:].replace(' ', '%20').upper()
