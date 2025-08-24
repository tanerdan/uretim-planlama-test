# backend/production/urls.py
from. import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MusteriViewSet, UrunViewSet

router = DefaultRouter()
router.register(r'musteriler', MusteriViewSet)
router.register(r'urunler', UrunViewSet)
router.register(r'siparisler', views.SiparisViewSet)
router.register(r'siparis-kalemleri', views.SiparisKalemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ulkeler/', views.ulke_listesi, name='ulke-listesi'),
    
    # Kur API'leri
    path('exchange-rates/', views.exchange_rates, name='exchange-rates'),
    path('convert-currency/', views.convert_currency, name='convert-currency'),
    path('currencies/', views.currency_list, name='currency-list'),
]