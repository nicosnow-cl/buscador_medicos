from django.urls import path

from . import views

urlpatterns = [
    path('', views.mainView, name = 'home'),
    path('get_comunas/', views.getComunas, name = 'get_comunas'),
    path('get_hospitales/', views.getHospitales, name = 'get_hospitales'),
    path('get_medicos/', views.getMedicos, name = 'get_medicos'),
    path('get_datos_medico/', views.getDatosMedico, name = 'get_datos_medico')
]