from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Restoran(models.Model):
    nomi = models.CharField(max_length=255, verbose_name=_('nomi'))
    manzil = models.TextField(verbose_name=_('manzil'))
    telefon = models.CharField(max_length=20, verbose_name=_('telefon'))
    ish_vaqti = models.CharField(max_length=100, verbose_name=_('ish vaqti'))
    image = models.ImageField(upload_to='images/', verbose_name=_('image'))

    class Meta:
        db_table = 'restoran'
        verbose_name = 'Restoran'
        verbose_name_plural = 'Restoran'

    def __str__(self):
        return self.nomi


class Xodimlar(models.Model):
    ism = models.CharField(max_length=100, verbose_name=_('ism'))
    familiya = models.CharField(max_length=100, verbose_name=_('familiya'))
    lavozim = models.CharField(max_length=100, verbose_name=_('lavozim'))
    ish_vaqti = models.CharField(max_length=100, verbose_name=_('ish vaqti'))
    restoran = models.ForeignKey(Restoran, on_delete=models.CASCADE, verbose_name=_('restoran'))

    class Meta:
        db_table = 'xodimlar'
        verbose_name = 'Xodim'
        verbose_name_plural = 'Xodimlar'

    def __str__(self):
        return f"{self.ism} - {self.lavozim}"


class Taomlar(models.Model):
    objects = models.Manager()
    nomi = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('nomi'))
    narx = models.IntegerField(null=True, blank=True, verbose_name=_('narx'))
    tavsif = models.TextField(null=True, blank=True, verbose_name=_('tavsif'))
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name=_('image'))

    class Meta:
        db_table = 'taomlar'
        verbose_name = 'Taom'
        verbose_name_plural = 'Taomlar'

    def __str__(self):
        return self.nomi


class Buyurtma(models.Model):
    objects = models.Manager()
    mijoz = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('mijoz'))
    restoran = models.ForeignKey(Restoran, on_delete=models.CASCADE, verbose_name=_('restoran'))
    taomlar = models.ManyToManyField(Taomlar, through='BuyurtmaTafsiloti', verbose_name=_('mahsulotlar'))
    manzil = models.TextField(null=True, blank=True, verbose_name=_('manzil'))
    miqdor = models.IntegerField(null=True, blank=True, verbose_name=_('miqdor'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'buyurtmalar'
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'

    def __str__(self):
        return f"{self.mijoz} - {self.restoran}"


class BuyurtmaTafsiloti(models.Model):
    objects = models.Manager()
    buyurtma = models.ForeignKey(Buyurtma, on_delete=models.CASCADE, verbose_name=_('buyurtma'))
    taom = models.ForeignKey(Taomlar, on_delete=models.CASCADE, verbose_name=_('mahsulot'))
    miqdor = models.IntegerField(null=True, blank=True, verbose_name=_('miqdor'))
    narx = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'buyurtma_tafsiloti'
        verbose_name = 'Buyurtma Tafsiloti'
        verbose_name_plural = 'Buyurtma Tafsilotlari'

    def __str__(self):
        return f"{self.buyurtma} - {self.taom} ({self.miqdor} dona)"


class MoliyaviyHisobot(models.Model):
    objects = models.Manager()
    restoran = models.ForeignKey(Restoran, on_delete=models.CASCADE, verbose_name=_('restoran'))
    tushum = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('tushum'))
    xarajat = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('xarajat'))
    sanasi = models.DateField(auto_now_add=True, verbose_name=_('sanasi'))

    class Meta:
        db_table = 'moliyaviy_hisobot'
        verbose_name = 'Moliyaviy Hisobot'
        verbose_name_plural = 'Moliyaviy Hisobotlar'

    def __str__(self):
        return f"{self.sanasi} - {self.restoran}"


class Sertifikat(models.Model):
    objects = models.Manager()
    mahsulot_nomi = models.CharField(max_length=255, verbose_name=_('mahsulot'))
    tasdiqlovchi_organ = models.CharField(max_length=255, verbose_name=_('tasdiqlovchi'))
    berilgan_sana = models.DateField()

    class Meta:
        db_table = 'sertifikat'
        verbose_name = 'Sertifikat'
        verbose_name_plural = 'Sertifikatlar'

    def __str__(self):
        return self.mahsulot_nomi


class OvqatMonitoring(models.Model):
    objects = models.Manager()
    taom = models.ForeignKey(Taomlar, on_delete=models.CASCADE, verbose_name=_('taom'))
    sertifikat = models.ForeignKey(Sertifikat, on_delete=models.CASCADE, verbose_name=_('sertifikat'))
    oxirgi_yangilanish = models.DateField()

    class Meta:
        db_table = 'ovqat_monitoring'
        verbose_name = 'Ovqat Monitoring'
        verbose_name_plural = 'Ovqat Monitoringlar'


class UserMenuChoice(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Taomlar, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 dan 5 gacha baho

    def __str__(self):
        return f'{self.user.get_username()} → {self.menu.nomi}'
