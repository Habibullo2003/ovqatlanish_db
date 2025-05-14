from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

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
    nomi = models.CharField(max_length=255, verbose_name=_('nomi'))
    restoranlar = models.ManyToManyField(Restoran, related_name='taomlar', verbose_name=_('restoranlar'))
    narx = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('narx'))
    tavsif = models.TextField(null=True, blank=True, verbose_name=_('tavsif'))
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name=_('image'))

    class Meta:
        db_table = 'taomlar'
        verbose_name = 'Taom'
        verbose_name_plural = 'Taomlar'

    def __str__(self):
        return self.nomi


class Kuryer(models.Model):
    ism = models.CharField(max_length=50)
    familiya = models.CharField(max_length=50)
    telefon = models.CharField(max_length=20, validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Telefon raqami to'g'ri formatda bo'lishi kerak, masalan: +998901234567"
        )
    ])
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    band = models.BooleanField(default=False)  # Kuryer band yoki bo‘sh ekanligi
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ism} {self.familiya}"


class Buyurtma(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('assigned', 'Kuryer Belgilandi'),
        ('cancelled', 'Bekor Qilindi'),
        ('delivered', 'Yetkazib Berildi'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('status')
    )
    mijoz = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('mijoz'))
    restoran = models.ForeignKey(Restoran, on_delete=models.CASCADE, verbose_name=_('restoran'))
    taomlar = models.ManyToManyField(Taomlar, through='BuyurtmaTafsiloti', verbose_name=_('mahsulotlar'))
    kuryer = models.ForeignKey(Kuryer, on_delete=models.SET_NULL, null=True, blank=True)
    manzil = models.TextField(null=True, blank=True, verbose_name=_('manzil'))
    payment_type = models.CharField(max_length=50, verbose_name=_('to‘lov turi'))
    promo_code = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('promokod'))
    distance_km = models.FloatField(null=True, blank=True, verbose_name=_('masofa'))
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('yetkazib berish narxi'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('umumiy narx'))
    order_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('yaratilgan vaqt'))
    additional_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        db_table = 'buyurtmalar'
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'

    def __str__(self):
        return f"{self.mijoz} - {self.restoran}"

    def check_timeout_and_cancel(self):
        """
        Buyurtma 5 daqiqadan ko‘p vaqt davomida 'pending' holatda qolsa,
        avtomatik tarzda 'cancelled' qilinadi.
        """
        if self.status == 'pending' and self.created_at:
            now = timezone.now()
            deadline = self.created_at + timedelta(minutes=5)
            if now > deadline:
                self.status = 'cancelled'
                self.save()


class BuyurtmaTafsiloti(models.Model):
    buyurtma = models.ForeignKey(Buyurtma, on_delete=models.CASCADE, verbose_name=_('buyurtma'))
    taom = models.ForeignKey(Taomlar, on_delete=models.CASCADE, verbose_name=_('mahsulot'))
    miqdor = models.IntegerField(verbose_name=_('miqdor'))
    narx = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('narx'))

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
