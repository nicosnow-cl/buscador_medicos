from django.urls import path

from tarea_3.views import *

app_name = 'tarea_3'

urlpatterns = [
    path('', mainView, name='main_view'),
    path('get_comunas/', getComunas, name='get_comunas'),
    path('get_hospitales/', getHospitales, name='get_hospitales'),
    path('get_medicos/', getMedicos, name='get_medicos'),
    path('get_datos_medico/', getDatosMedico, name='get_datos_medico')
]