from itertools import zip_longest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import ExtractMonth
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, F, Sum, Case, When, Value, CharField
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, CreateView
from .models import Taomlar, Buyurtma, Restoran, Xodimlar, Sertifikat, OvqatMonitoring
from .forms import BuyurtmaForm
from django.views import View


class HomeView(View):
    def get(self, request):
        foods = Taomlar.objects.all()
        return render(request, 'index.html', {'foods': foods})


class MenuView(View):
    template_name = 'menu.html'

    def get(self, request):
        foods = Taomlar.objects.all()
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
            Buyurtma.objects
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(
                total=Sum(F('taomlar__narx') * F('miqdor')),
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
        total_income = Buyurtma.objects.aggregate(total=Sum(F('taomlar__narx') * F('miqdor')))['total'] or 0

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
