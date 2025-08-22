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
]