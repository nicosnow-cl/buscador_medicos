from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from tarea_3.models import *

# Create your views here.
def mainView(request):
    data = {'regiones': Region.objects.all()}
    return render(request, 'index.html', data)

def getComunas(request):
    val = request.GET.get('region_id')
    data = Comuna.objects.filter(region_id=val).values()
    return JsonResponse({'comunas': list(data)})

def getHospitales(request):
    val = request.GET.get('comuna_id')
    data = {'hospitales': Hospital.objects.filter(comuna_id=val)}
    return render(request, 'response_content.html', data)

def getMedicos(request):
    from tarea_3.scrapper_transparencia import ScraperTransparencia

    val = request.GET.get('hospital_id')
    data_hospital = {'hospital': Hospital.objects.filter(id=val)}
    data_comuna = {'comuna': Comuna.objects.filter(id=data_hospital['hospital'][0].comuna_id)}
    web_scraper = ScraperTransparencia(data_hospital['hospital'][0].name, data_comuna['comuna'][0].name, True)
    encontrado, data = web_scraper.run()

    if not encontrado:
        data = {'medico': 'SIN RESULTADOS'}

    return render(request, 'table_medicos.html', {'medicos': dict(data)})

def getDatosMedico(request):
    from tarea_3.scraper_ryf import ScraperRYF
    from tarea_3.request_superdesalud import APISuperDeSalud

    nombre = request.GET.get('nombre')
    web_scraper = ScraperRYF(nombre, True)
    encontrado, rut = web_scraper.run()

    if encontrado:
        api = APISuperDeSalud(rut)
        data = api.run()
    else:
        data = {'antecedentes': 'NO ENCONTRADO'}

    return render(request, 'datos_medico.html', {'medico': dict(data)})