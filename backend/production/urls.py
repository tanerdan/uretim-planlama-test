# backend/production/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register all ViewSets
router = DefaultRouter()
router.register(r'musteriler', views.MusteriViewSet)
router.register(r'urunler', views.UrunViewSet)
router.register(r'siparisler', views.SiparisViewSet)
router.register(r'siparis-kalemleri', views.SiparisKalemViewSet)

# Production ViewSets
router.register(r'istasyonlar', views.IsIstasyonuViewSet)
router.register(r'standart-is-adimlari', views.StandardIsAdimiViewSet)
router.register(r'is-akislari', views.IsAkisiViewSet)
router.register(r'is-emirleri', views.IsEmriViewSet)
router.register(r'urun-receteleri', views.UrunReceteViewSet, basename='urunrecete')
router.register(r'bom-templates', views.BOMTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Manual function-based endpoints  
    path('ulkeler/', views.ulke_listesi, name='ulke-listesi'),
    path('istasyon-listesi/', views.istasyon_listesi, name='istasyon-listesi'),
    path('exchange-rates/', views.exchange_rates, name='exchange-rates'),
    path('convert-currency/', views.convert_currency, name='convert-currency'),
    path('currencies/', views.currency_list, name='currency-list'),
]