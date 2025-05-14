import json
import logging
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
from itertools import zip_longest
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.conf import settings
from main.ai.forecast import get_order_forecast
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, F, Sum, Case, When, Value, CharField
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView, CreateView, DetailView
from .models import Xodimlar, Sertifikat, OvqatMonitoring, Buyurtma, BuyurtmaTafsiloti, Restoran, Taomlar, Kuryer
from .forms import BuyurtmaForm
from django.views import View
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class HomeView(View):
    def get(self, request):
        foods = Taomlar.objects.all()
        return render(request, 'index.html', {'foods': foods})


class MenuView(View):
    template_name = 'menu.html'

    def get(self, request):
        # Taomlarni va ularga bog'langan restoranlarni birgalikda yuklaymiz
        foods = Taomlar.objects.all().prefetch_related('restoranlar')
        return render(request, self.template_name, {'foods': foods})


class BuyurtmaCreateView(LoginRequiredMixin, CreateView):
    model = Buyurtma
    form_class = BuyurtmaForm
    template_name = 'orders.html'
    success_url = reverse_lazy('orders')

    def form_valid(self, form):
        buyurtma = form.save(commit=False)
        buyurtma.mijoz = self.request.user
        buyurtma.save()

        messages.success(self.request, "Buyurtma muvaffaqiyatli qo‘shildi!")
        return redirect(super().form_valid(form))

    def form_invalid(self, form):
        messages.error(self.request, "Xatolik yuz berdi! Formani to‘g‘ri to‘ldiring.")
        return redirect(super().form_valid(form))


class AnalyticsView(View):
    template_name = 'analytics.html'

    def get(self, request, *args, **kwargs):
        # Eng ko‘p buyurtma qilingan 5 ta taom
        top_dishes = (
            Taomlar.objects
            .annotate(total_orders=Count('buyurtma'))
            .order_by('-total_orders')[:5]
        )

        # Oylik daromad statistikasi
        monthly_income = (
            BuyurtmaTafsiloti.objects
            .annotate(month=ExtractMonth('buyurtma__created_at'))
            .values('month')
            .annotate(
                total=Sum(F('taom__narx') * F('miqdor')),
                month_name=Case(
                    *[
                        When(month=i, then=Value(name))
                        for i, name in enumerate(
                            ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
                             "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"], 1)
                    ],
                    output_field=CharField()
                )
            )
            .order_by('month')
        )

        # Umumiy buyurtmalar soni va jami daromad
        total_orders = Buyurtma.objects.count()
        total_income = BuyurtmaTafsiloti.objects.aggregate(total=Sum(F('taom__narx') * F('miqdor')))['total'] or 0

        # Eng faol mijozlar (ko'p buyurtma berganlar)
        top_customers = (
            Buyurtma.objects.values('mijoz__username')
            .annotate(order_count=Count('id'))
            .order_by('-order_count')[:5]  # Eng faol 5 mijoz
        )

        # Kontekstga ma'lumotlarni kiritish
        context = {
            'top_dishes': list(top_dishes),
            'monthly_income': list(monthly_income),
            'total_orders': total_orders,
            'total_income': total_income,
            'top_customers': top_customers,
        }

        return render(request, self.template_name, context)


class RestoranView(ListView):
    model = Restoran
    template_name = 'restaurants.html'  # HTML shablon fayli
    context_object_name = 'restaurants'  # Shablonda foydalaniladigan o‘zgaruvchi nomi


class XodimlarView(ListView):
    model = Xodimlar
    template_name = 'employees.html'  # Shablon fayli
    context_object_name = 'employees'  # Shablonda foydalaniladigan o‘zgaruvchi nomi


class HisobotlarView(TemplateView):
    template_name = 'finance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sertifikatlar'] = Sertifikat.objects.all()
        ovqat_monitoringlari = OvqatMonitoring.objects.all()
        top_dishes = (
            Taomlar.objects
            .annotate(total_orders=Count('buyurtma')).order_by('-total_orders')
        )
        combined_data = zip_longest(ovqat_monitoringlari, top_dishes, fillvalue=None)
        context['combined_data'] = combined_data
        return context


class TestView(TemplateView):
    template_name = "success.html"

    def get(self, request, *args, **kwargs):
        messages.success(request, "Xabar ishlayapti!")  # Xabar qo'shish
        return render(request, 'success.html')


DISTANCES = {
    'Chilonzor': 5,
    'Yunusobod': 10,
    'Mirzo Ulugbek': 8,
    'Yakkasaroy': 6,
    'Olmazor': 7,
    'Mirobod': 4,
    'Sergeli': 12,
    'Bektemir': 15,
    'Shayxontohur': 5
}


class OrderView(View):
    template_name = 'order.html'

    def get(self, request, food_id, restaurant_id):
        try:
            food = Taomlar.objects.get(id=food_id)
            restaurant = Restoran.objects.get(id=restaurant_id)

            # Savatni tekshirish va yangilash
            cart = request.session.get('cart', [])
            current_item = next((item for item in cart if item['taom_id'] == food_id), None)
            initial_quantity = current_item['count'] if current_item else 1

            return render(request, self.template_name, {
                'food': food,
                'restaurant': restaurant,
                'initial_quantity': initial_quantity,
                'current_restaurant_id': restaurant_id
            })
        except (Taomlar.DoesNotExist, Restoran.DoesNotExist):
            messages.error(request, _("Taom yoki restoran topilmadi"))
            return redirect('menu')

    def post(self, request, food_id, restaurant_id):
        if not request.user.is_authenticated:
            messages.error(request, _("Buyurtma berish uchun tizimga kiring"))
            return redirect('login')

        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                raise ValueError(_("Miqdor noto'g'ri"))

            # Savatni yangilash
            cart = request.session.get('cart', [])
            existing_item = next((item for item in cart if item['taom_id'] == food_id), None)

            if existing_item:
                existing_item['count'] = quantity
            else:
                cart.append({
                    'taom_id': food_id,
                    'count': quantity,
                    'restaurant_id': restaurant_id
                })

            request.session['cart'] = cart
            request.session['current_restaurant_id'] = restaurant_id
            request.session.modified = True

            messages.success(request, _("Savat yangilandi!"))
            return redirect('checkout')

        except (ValueError, TypeError) as e:
            messages.error(request, _("Noto'g'ri miqdor kiritildi"))
            return redirect('order', food_id=food_id, restaurant_id=restaurant_id)


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        # Initial checks before rendering the context
        user = self.request.user
        cart = self.request.session.get('cart', [])
        restaurant_id = self.request.session.get('current_restaurant_id')

        # Safeguard against invalid restaurant_id
        if not restaurant_id or not isinstance(restaurant_id, (int, str)):
            messages.error(request, _("Restoran tanlanmagan yoki noto‘g‘ri"))
            return redirect('menu')

        try:
            restaurant_id = int(restaurant_id)  # Ensure it's an integer
            restaurant = Restoran.objects.get(id=restaurant_id)
        except (ValueError, Restoran.DoesNotExist):
            messages.error(request, _("Restoran topilmadi"))
            return redirect('menu')

        # If checks pass, proceed to get context
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cart = self.request.session.get('cart', [])
        restaurant_id = self.request.session.get('current_restaurant_id')

        # Taomlarni bazadan qayta yuklash
        cart_items = []
        subtotal = Decimal('0')
        for item in cart:
            try:
                taom = Taomlar.objects.get(id=item.get('taom_id'))
                count = item.get('count', 1)
                narx = taom.narx
                cart_items.append({
                    'taom': taom,
                    'count': count,
                    'narx': narx
                })
                subtotal += Decimal(narx) * count
            except Taomlar.DoesNotExist:
                continue

        # Foydalanuvchining birinchi buyurtmasi ekanligini va promokoddan foydalanganligini tekshirish
        is_first_order = not Buyurtma.objects.filter(mijoz=user).exists()
        has_used_promo = Buyurtma.objects.filter(mijoz=user, promo_code='welcome').exists()
        can_use_promo = is_first_order and not has_used_promo

        # Dastlabki yetkazib berish narxi (manzil hali tanlanmagan)
        delivery_fee = Decimal('0')  # Manzil tanlanganda POST'da hisoblanadi
        discount = Decimal('0')  # POST'da hisoblanadi

        context.update({
            'cart_items': cart_items,
            'is_first_order': is_first_order,
            'can_use_promo': can_use_promo,
            'restaurant_id': restaurant_id,
            'distances': settings.DELIVERY_DISTANCES,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'discount': discount,
            'total_price': subtotal,
        })
        return context

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, _("Buyurtma berish uchun tizimga kiring"))
            return redirect('login')

        user = request.user
        cart = request.session.get('cart', [])
        restaurant_id = request.session.get('current_restaurant_id')

        if not cart:
            messages.error(request, _("Savat bo'sh!"))
            return redirect('checkout')

        # Restoran tekshiruvi
        try:
            restaurant_id = int(restaurant_id)  # Ensure it's an integer
            restaurant = Restoran.objects.get(id=restaurant_id)
        except (ValueError, Restoran.DoesNotExist):
            messages.error(request, _("Restoran topilmadi"))
            return redirect('checkout')

        # Ma'lumotlarni olish
        address = request.POST.get('address')
        if not address:
            messages.error(request, _("Manzilni tanlash majburiy!"))
            return redirect('checkout')

        payment_type = request.POST.get('payment_type', 'cash')
        promo_code = (request.POST.get('promo_code') or '').strip().lower()
        order_time_str = request.POST.get('order_time')
        agree_to_minimum_fee = request.POST.get('agree_to_minimum_fee', 'off') == 'on'

        # Buyurtma vaqtini tekshirish
        if not order_time_str:
            messages.error(request, _("Buyurtma vaqtini tanlash majburiy!"))
            return redirect('checkout')

        try:
            order_time = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M')
            order_time = timezone.make_aware(order_time, timezone.get_current_timezone())
            if order_time <= timezone.now():
                messages.error(request, _("Buyurtma vaqti hozirgi vaqtdan keyin bo‘lishi kerak!"))
                return redirect('checkout')
        except ValueError:
            messages.error(request, _("Noto‘g‘ri vaqt formati!"))
            return redirect('checkout')

        # Narxlarni hisoblash
        cart_items = []
        subtotal = Decimal('0')
        for item in cart:
            try:
                taom = Taomlar.objects.get(id=item.get('taom_id'))
                count = item.get('count', 1)
                cart_items.append({
                    'taom': taom,
                    'count': count,
                    'narx': taom.narx
                })
                subtotal += Decimal(taom.narx) * count
            except Taomlar.DoesNotExist:
                continue

        # Minimal buyurtma miqdorini tekshirish (40,000 so'm)
        MINIMUM_ORDER_AMOUNT = Decimal('40000')
        additional_fee = Decimal('0')

        if subtotal < MINIMUM_ORDER_AMOUNT:
            if not agree_to_minimum_fee:
                messages.error(request, _(
                    "Buyurtma summasi 40,000 so'mdan kam! Iltimos, ko'proq mahsulot tanlang yoki minimal to'lovga rozilik bering."
                ))
                return redirect('checkout')
            else:
                additional_fee = MINIMUM_ORDER_AMOUNT - subtotal

        # Yetkazib berish narxi
        distance_km = settings.DELIVERY_DISTANCES.get(address, 0)
        is_first_order = not Buyurtma.objects.filter(mijoz=user).exists()
        per_km_fee = getattr(settings, 'PER_KM_FEE', Decimal('2000'))
        delivery_fee = Decimal('0') if is_first_order else Decimal(distance_km) * per_km_fee

        # Chegirma hisoblash
        discount = Decimal('0')
        minimum_order_for_discount = getattr(settings, 'MINIMUM_ORDER_FOR_DISCOUNT', Decimal('80000'))
        has_used_promo = Buyurtma.objects.filter(mijoz=user, promo_code='welcome').exists()

        if promo_code == 'welcome':
            if not is_first_order:
                messages.warning(request, _("Promokod faqat 1-buyurtma uchun amal qiladi!"))
            elif has_used_promo:
                messages.warning(request, _("Siz allaqachon WELCOME promokodidan foydalanib bo'lgansiz!"))
            elif subtotal < minimum_order_for_discount:
                messages.warning(request, _("Minimal buyurtma miqdori yetarli emas!"))
            else:
                discount = subtotal * Decimal('0.5')
                messages.success(request, _("50% chegirma qo'llandi!"))
        elif promo_code:
            messages.warning(request, _("Noto'g'ri promokod!"))

        # Yakuniy narx (qo'shimcha to'lovni hisobga olamiz)
        final_price = (subtotal - discount) + delivery_fee + additional_fee

        # Buyurtma yaratish
        try:
            buyurtma = Buyurtma.objects.create(
                mijoz=user,
                restoran=restaurant,
                manzil=address,
                payment_type=payment_type,
                promo_code=promo_code if discount > 0 else None,
                distance_km=distance_km,
                delivery_price=delivery_fee,
                total_price=final_price,
                order_time=order_time,
                status='pending',
                additional_fee=additional_fee
            )

            # Buyurtma tafsilotlarini yaratish
            for item in cart_items:
                BuyurtmaTafsiloti.objects.create(
                    buyurtma=buyurtma,
                    taom=item['taom'],
                    miqdor=item['count'],
                    narx=item['taom'].narx
                )

            # Savatni tozalash
            request.session['cart'] = []
            request.session['current_restaurant_id'] = None
            request.session.modified = True

            return redirect('order_success')

        except Exception as e:
            messages.error(request, _("Buyurtma jarayonida xato: {}").format(str(e)))
            return redirect('checkout')


class RestaurantDishesView(DetailView):
    model = Restoran
    template_name = 'restaurant_dishes.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dishes = self.object.taomlar.all()
        context['dishes'] = dishes
        context['restaurant_id'] = self.object.id
        self.request.session['current_restaurant_id'] = self.object.id
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SaveCartView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

        cart = data.get('cart', [])
        if not isinstance(cart, list):
            return JsonResponse({'status': 'error', 'message': 'Cart must be a list'}, status=400)

        required_fields = {'taom_id', 'name', 'narx', 'count'}
        for item in cart:
            if not isinstance(item, dict):
                return JsonResponse({'status': 'error', 'message': 'Each cart item must be a dictionary'}, status=400)
            if not all(field in item for field in required_fields):
                return JsonResponse(
                    {'status': 'error', 'message': 'Each cart item must contain taom_id, name, narx, and count'},
                    status=400)
            try:
                float(item['narx'])
                int(item['count'])
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid narx or count value'}, status=400)

        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Cart saved to session'})


@method_decorator(csrf_exempt, name='dispatch')
class SaveRestaurantIdView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

        # Extract restaurant_id, handling potential nesting
        restaurant_id = data.get('restaurant_id')
        if isinstance(restaurant_id, dict):
            restaurant_id = restaurant_id.get('restaurant_id')  # Handle nested case
        if not restaurant_id:
            return JsonResponse({'status': 'error', 'message': 'Restaurant ID is required'}, status=400)

        # Convert to integer if possible
        try:
            restaurant_id = int(restaurant_id)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Restaurant ID must be a valid number'}, status=400)

        request.session['current_restaurant_id'] = restaurant_id
        return JsonResponse({'status': 'success', 'message': 'Restaurant ID saved to session'})


@method_decorator(csrf_exempt, name='dispatch')
class ClearCartView(View):
    def post(self, request, *args, **kwargs):
        request.session['cart'] = []
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Cart cleared from session'})


class OrderSuccessView(TemplateView):
    template_name = 'order_success.html'


class ContactCourierView(TemplateView):
    template_name = 'contact_courier.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        buyurtma = Buyurtma.objects.filter(mijoz=user).order_by('-created_at').first()
        if not buyurtma:
            messages.error(request, _("Buyurtma topilmadi!"))
            return redirect('home')

        context = self.get_context_data(**kwargs)
        context['buyurtma'] = buyurtma
        return self.render_to_response(context)


def check_order_status(request, buyurtma_id):
    buyurtma = get_object_or_404(Buyurtma, id=buyurtma_id)
    time_elapsed = timezone.now() - buyurtma.created_at
    five_minutes = timedelta(minutes=5)

    if time_elapsed >= five_minutes and buyurtma.status == 'pending' and not buyurtma.kuryer:
        buyurtma.is_cancelled = True  # Mark as canceled
        buyurtma.save()

    return JsonResponse({
        'status': buyurtma.status,
        'has_courier': bool(buyurtma.kuryer),
        'is_cancelled': buyurtma.is_cancelled,
    })


def cancel_order(request, buyurtma_id):
    buyurtma = get_object_or_404(Buyurtma, id=buyurtma_id)
    if buyurtma.status == 'pending':
        buyurtma.is_cancelled = True  # Mark as canceled
        buyurtma.save()
        messages.success(request, "Buyurtma bekor qilindi!")
    return redirect('contact_courier', buyurtma_id=buyurtma_id)


class BuyurtmaDetailView(DetailView):
    model = Buyurtma
    template_name = 'buyurtma_detail.html'
    context_object_name = 'buyurtma'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buyurtma = self.get_object()
        if buyurtma.status == 'pending':
            context['rasmiylashtirilsin'] = True
        return context


logger = logging.getLogger(__name__)


class OrderForecastView(AnalyticsView):
    template_name = 'dashboard/forecast.html'

    def get(self, request, *args, **kwargs):
        # Ota klass (AnalyticsView) dan render natijasini olish
        response = super().get(request, *args, **kwargs)
        # Agar response HttpResponse bo'lsa, uni qaytarish
        return response


class CourierSelectionView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Kuryer
    template_name = 'courier_selection.html'
    context_object_name = 'couriers'

    def test_func(self):
        # Faqat admin foydalanuvchilar kirishi mumkin
        return self.request.user.is_staff

    def get_queryset(self):
        # Faqat bo'sh kuryerlar ro'yxatini olish
        return Kuryer.objects.filter(band=True).order_by('-rating')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buyurtma_id = self.kwargs.get('buyurtma_id')
        buyurtma = get_object_or_404(Buyurtma, id=buyurtma_id)
        context['buyurtma'] = buyurtma
        return context


class AssignCourierView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        # Faqat admin foydalanuvchilar kirishi mumkin
        return self.request.user.is_staff

    def post(self, request, buyurtma_id, courier_id):
        buyurtma = get_object_or_404(Buyurtma, id=buyurtma_id)
        kuryer = get_object_or_404(Kuryer, id=courier_id, band=True)

        # Kuryerni buyurtmaga tayinlash
        buyurtma.kuryer = kuryer  # `couriers` o‘rniga `kuryer`
        buyurtma.status = 'assigned'  # `3` o‘rniga `assigned`
        buyurtma.save()

        # Kuryerni band qilish
        kuryer.band = False
        kuryer.save()

        messages.success(request, f"Kuryer {kuryer} buyurtmaga muvaffaqiyatli tayinlandi!")
        return redirect('admin:main_buyurtma_change', buyurtma.id)  # Admin panelga qaytish