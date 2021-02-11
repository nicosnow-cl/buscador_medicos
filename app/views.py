from django.http import JsonResponse
from django.shortcuts import render
from json import dumps 
from .models import *

def mainView(request):
    data_regions = {'regiones': Region.objects.all()}
    return render(request, 'index.html', data_regions)

def getComunas(request):
    id = request.GET.get('region_id')
    data_comunas = Comuna.objects.filter(region_id = id).values()
    return JsonResponse({'comunas': list(data_comunas)})

def getHospitales(request):
    id = request.GET.get('comuna_id')
    data_hospitales = {'hospitales': Hospital.objects.filter(comuna_id = id)}
    return render(request, 'response_content.html', data_hospitales)

def getMedicos(request):
    from .scrapers.scraper_transparencia import ScraperTransparencia
    from .general_functions.strings import chileanCurrency, toGoogleSearch, toDoctoraliaSearch
    id = request.GET.get('hospital_id')
    data_hospital = {'hospital': Hospital.objects.filter(hospital_id = id)}
    data_comuna = {'comuna': Comuna.objects.filter(comuna_id = data_hospital['hospital'][0].comuna_id_id)}
    scraper_portal_transparencia = ScraperTransparencia(data_hospital['hospital'][0].hospital_name, data_comuna['comuna'][0].comuna_name, True)
    encontrado, data_medicos = scraper_portal_transparencia.run()    
    if not encontrado: data_medicos = {'error': 'SIN RESULTADOS'}
    list_medicos = scraper_portal_transparencia.transformDictToList(data_medicos)
    for idx in range(len(list_medicos)):
        # print(idx)
        # print(list_medicos[idx]['REMUNERACION'])        
        list_medicos[idx]['REMUNERACION'] = chileanCurrency(list_medicos[idx]['REMUNERACION'])
        list_medicos[idx]['GOOGLE_SEARCH'] = toGoogleSearch(list_medicos[idx]['NOMBRE'])
        list_medicos[idx]['DOCTORALIA_SEARCH'] = toDoctoraliaSearch(list_medicos[idx]['NOMBRE'])
    return render(request, 'table_medicos.html', {'medicos': dumps(list_medicos)})

def getDatosMedico(request):
    from .superdesalud.api_superdesalud import APISuperDeSalud
    from .scrapers.scraper_ryf import ScraperRyF
    # from .scrapers.scraper_superdesalud import ScraperSuperDeSalud # Desafortunadamente la página de SuperdeSalud incorporo un Captcha
    # super_de_salud_scraper = ScraperSuperDeSalud(nombre_medico, True)
    # encontrado, rut = super_de_salud_scraper.getRutMedico()
    nombre_medico = request.GET.get('nombre')
    rut_firma_scraper = ScraperRyF(nombre_medico, True)
    rut_encontrado, rut = rut_firma_scraper.getRut()
    if rut_encontrado:        
        super_de_salud_api = APISuperDeSalud(rut)
        antecedentes_medico = super_de_salud_api.getAntecedentes()
        if not antecedentes_medico: antecedentes_medico = {'antecedentes': 'NO ENCONTRADO'}
    else:
        antecedentes_medico = {'antecedentes': 'NO ENCONTRADO'}
    print(antecedentes_medico)
    return render(request, 'datos_medico.html', {'medico': dict(antecedentes_medico)})
