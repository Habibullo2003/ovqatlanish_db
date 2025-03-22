from django.contrib import admin
from .models import Restoran, Taomlar, Buyurtma, BuyurtmaTafsiloti, MoliyaviyHisobot, Xodimlar, Sertifikat, OvqatMonitoring
# Register your models here.
admin.site.register((Restoran, Taomlar, Buyurtma, BuyurtmaTafsiloti, MoliyaviyHisobot, Xodimlar, Sertifikat, OvqatMonitoring))