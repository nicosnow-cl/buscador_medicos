from django.db import models
import json

# Create your models here.
class Region(models.Model):
    number = models.CharField(max_length=3, verbose_name='Número', null=False, unique=True)
    name = models.CharField(max_length=100, verbose_name='Nombre', null=False)

    def __str__(self):
        return json.dumps([self.id, self.number, self.name], ensure_ascii=False)

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regiones'
        db_table = 'region'
        ordering = ['id']

class Comuna(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Nombre', null=False)

    def __str__(self):
        return json.dumps([self.id, self.region_id, self.name], ensure_ascii=False)

    class Meta:
        verbose_name = 'Comuna'
        verbose_name_plural = 'Comunas'
        db_table = 'comuna'
        ordering = ['id']

class Hospital(models.Model):
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name='Nombre', null=False)

    def __str__(self):
        return json.dumps([self.id, self.comuna_id, self.name], ensure_ascii=False)

    class Meta:
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitales'
        db_table = 'hospital'
        ordering = ['id']
