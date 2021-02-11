from django.db import models

class Region(models.Model):   
    region_id = models.IntegerField(primary_key = True) 
    region_number = models.CharField(max_length = 4, null = False)
    region_name = models.CharField(max_length = 255, null = False)

class Comuna(models.Model):
    comuna_id = models.IntegerField(primary_key = True) 
    comuna_name = models.CharField(max_length = 255, null = False)
    region_id = models.ForeignKey(Region, on_delete = models.CASCADE, null = False)

class Hospital(models.Model):
    hospital_id = models.IntegerField(primary_key = True) 
    hospital_name = models.CharField(max_length = 255, null = False)
    hospital_image_path = models.CharField(max_length = 255, null = True)
    comuna_id = models.ForeignKey(Comuna, on_delete = models.CASCADE, null = False)

class Medic(models.Model):    
    medic_id = models.IntegerField(primary_key = True)
    medic_name = models.CharField(max_length = 255, null = False)
    medic_type = models.CharField(max_length = 25, null = False)
    medic_position =  models.CharField(max_length = 30, null = False)
    medic_remuneration = models.IntegerField()
    hospital_id = models.ForeignKey(Hospital, on_delete = models.CASCADE, null = False)

class HospitalLastUpdate(models.Model):
    last_update_id = models.IntegerField(primary_key = True)
    last_update_datetime = models.DateTimeField(auto_now = True, null = False)
    hospital_id = models.ForeignKey(Hospital, on_delete = models.CASCADE, null = False)