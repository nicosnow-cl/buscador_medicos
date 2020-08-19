from app.wsgi import *
from django.test import TestCase

# Create your tests here.
from tarea_3 import models
import json

file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'initial_data')
file_name = 'initial_data_fixture.json'

regiones_comunas = json.load(open(os.path.join(file_path, file_name), encoding = 'utf-8'))
comunas_pk = 1

for num, region in enumerate(regiones_comunas):
    object, was_created = models.Region.objects.get_or_create(number=region['numero'], name=region['region'])
    print(str(object))

    for comuna in region['comunas']:
        object, was_created = models.Comuna.objects.get_or_create(name=comuna, region_id=num+1)
        print('     ' + str(object))

        for hospital in region['comunas'][comuna]:
            object, was_created = models.Hospital.objects.get_or_create(comuna_id=comunas_pk, name=hospital)
            print('          ' + str(object))
        comunas_pk += 1
