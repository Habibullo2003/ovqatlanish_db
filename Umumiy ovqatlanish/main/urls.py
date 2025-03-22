from django.urls import path
from .views import HomeView, MenuView, BuyurtmaCreateView, AnalyticsView, RestoranView, XodimlarView, HisobotlarView, TestView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('orders/', BuyurtmaCreateView.as_view(), name='orders'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('restaurants/', RestoranView.as_view(), name='restaurants'),
    path('employees/', XodimlarView.as_view(), name='employees'),
    path('finance/', HisobotlarView.as_view(), name='finance'),
    path('test/', TestView.as_view(), name='test'),
]
