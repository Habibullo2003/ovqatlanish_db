from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Restoran, Taomlar, Buyurtma, BuyurtmaTafsiloti, MoliyaviyHisobot, Xodimlar, Sertifikat, \
    OvqatMonitoring, UserMenuChoice, Kuryer

# Register your models here.
admin.site.register((MoliyaviyHisobot, Xodimlar, Sertifikat, OvqatMonitoring, UserMenuChoice))


@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mijoz', 'manzil', 'status', 'kuryer', 'is_cancelled_display', 'created_at', 'select_courier_link')
    list_filter = ('status', 'kuryer', 'is_cancelled')
    search_fields = ('mijoz__username', 'manzil')
    list_editable = ('status', 'kuryer')
    actions = ['assign_courier']

    def select_courier_link(self, obj):
        if obj.is_cancelled:
            return format_html('<span class="text-muted">Buyurtma bekor qilingan</span>')
        url = reverse('courier_selection', args=[obj.id])
        return format_html('<a href="{}" class="button">Kuryer Tanlash</a>', url)

    select_courier_link.short_description = "Kuryer Tanlash"

    def assign_courier(self, request, queryset):
        available_courier = Kuryer.objects.filter(band=True).order_by('-rating').first()
        if not available_courier:
            self.message_user(request, "Bo'sh kuryer topilmadi!", level='error')
            return

        updated = 0
        for buyurtma in queryset.filter(status='pending', is_cancelled=False):
            buyurtma.kuryer = available_courier
            buyurtma.status = 'assigned'
            buyurtma.save()
            available_courier.band = False
            available_courier.save()
            updated += 1

        self.message_user(request, f"{updated} ta buyurtmaga kuryer tayinlandi: {available_courier}.")

    assign_courier.short_description = "Tanlangan buyurtmalarga kuryer tayinlash"

    def is_cancelled_display(self, obj):
        return 'Ha' if obj.is_cancelled else 'Yo‘q'

    is_cancelled_display.short_description = "Bekor Qilingan"
    is_cancelled_display.admin_order_field = 'is_cancelled'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('kuryer')


@admin.register(Kuryer)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('ism', 'familiya', 'telefon', 'rating', 'band')
    list_filter = ('band', 'rating')
    search_fields = ('ism', 'familiya', 'telefon')
    actions = ['make_available', 'make_unavailable']

    def make_available(self, request, queryset):
        updated = queryset.update(band=True)
        self.message_user(request, f"{updated} ta kuryer bo'sh qilindi.")

    make_available.short_description = "Tanlangan kuryerlarni bo'sh qilish"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(band=False)
        self.message_user(request, f"{updated} ta kuryer band qilindi.")

    make_unavailable.short_description = "Tanlangan kuryerlarni band qilish"


@admin.register(Restoran)
class RestoranAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'manzil')


@admin.register(Taomlar)
class TaomlarAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'get_restoranlar']
    list_filter = ['restoranlar']  # ManyToManyField bo‘lsa bo'ladi

    def get_restoranlar(self, obj):
        return ", ".join([r.nomi for r in obj.restoranlar.all()])

    get_restoranlar.short_description = "Restoranlar"


@admin.register(BuyurtmaTafsiloti)
class BuyurtmaTafsilotiAdmin(admin.ModelAdmin):
    list_display = ('buyurtma', 'taom', 'miqdor', 'narx')
