from django.urls import path
from .views import RecommendationView

urlpatterns = [
    path('recommend/', RecommendationView.as_view(), name='recommendation'),
]
