from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(Hospital)
admin.site.register(Medic)
admin.site.register(HospitalLastUpdate)
