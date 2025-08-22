# backend/production/views.py

from django.db import models
from rest_framework import viewsets, status,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Musteri, Urun, Siparis, SiparisKalem, SiparisDosya
from .serializers import (
    MusteriSerializer, UrunSerializer, 
    SiparisSerializer, SiparisCreateSerializer,
    SiparisKalemSerializer, SiparisDosyaSerializer
)



class MusteriViewSet(viewsets.ModelViewSet):
    """
    Müşteri CRUD işlemleri için ViewSet
    """
    queryset = Musteri.objects.all()
    serializer_class = MusteriSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['aktif']
    search_fields = ['ad', 'kod', 'email']
    ordering_fields = ['ad', 'kod', 'olusturulma_tarihi']
    ordering = ['ad']
    
    @action(detail=False, methods=['get'])
    def aktif_musteriler(self, request):
        """Sadece aktif müşterileri getir"""
        aktif = self.queryset.filter(aktif=True)
        serializer = self.get_serializer(aktif, many=True)
        return Response(serializer.data)

class UrunViewSet(viewsets.ModelViewSet):
    """
    Ürün CRUD işlemleri için ViewSet
    """
    queryset = Urun.objects.all()
    serializer_class = UrunSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['aktif', 'birim']
    search_fields = ['ad', 'kod', 'aciklama']
    ordering_fields = ['ad', 'kod', 'mevcut_stok']
    ordering = ['ad']
    
    @action(detail=False, methods=['get'])
    def stok_kritik(self, request):
        """Kritik stok seviyesindeki ürünleri getir"""
        kritik = self.queryset.filter(mevcut_stok__lte=models.F('minimum_stok'))
        serializer = self.get_serializer(kritik, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def stok_ekle(self, request, pk=None):
        """Ürüne stok ekle"""
        urun = self.get_object()
        miktar = request.data.get('miktar', 0)
        
        try:
            miktar = int(miktar)
            if miktar > 0:
                urun.mevcut_stok += miktar
                urun.save()
                return Response({
                    'status': 'success',
                    'yeni_stok': urun.mevcut_stok,
                    'message': f'{miktar} adet stok eklendi'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Miktar 0\'dan büyük olmalıdır'
                }, status=400)
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Geçersiz miktar'
            }, status=400)

class SiparisViewSet(viewsets.ModelViewSet):
    queryset = Siparis.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['siparis_no', 'musteri__ad']
    filterset_fields = ['durum', 'musteri', 'tarih']
    ordering_fields = ['tarih', 'teslim_tarihi', 'siparis_no']
    ordering = ['-tarih']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SiparisCreateSerializer
        return SiparisSerializer
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def dosya_ekle(self, request, pk=None):
        """Siparişe dosya ekleme endpoint'i"""
        siparis = self.get_object()
        dosya = request.FILES.get('dosya')
        aciklama = request.data.get('aciklama', '')
        
        if not dosya:
            return Response({'error': 'Dosya gerekli'}, status=status.HTTP_400_BAD_REQUEST)
        
        siparis_dosya = SiparisDosya.objects.create(
            siparis=siparis,
            dosya=dosya,
            aciklama=aciklama
        )
        
        serializer = SiparisDosyaSerializer(siparis_dosya)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def kalemler(self, request, pk=None):
        """Siparişin kalemlerini getir"""
        siparis = self.get_object()
        kalemler = siparis.kalemler.all()
        serializer = SiparisKalemSerializer(kalemler, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def bekleyen_siparisler(self, request):
        """Bekleyen siparişleri listele"""
        siparisler = self.queryset.filter(durum='beklemede')
        serializer = self.get_serializer(siparisler, many=True)
        return Response(serializer.data)

class SiparisKalemViewSet(viewsets.ModelViewSet):
    queryset = SiparisKalem.objects.all()
    serializer_class = SiparisKalemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['siparis', 'urun']