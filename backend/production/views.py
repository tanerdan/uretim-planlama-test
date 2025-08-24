# backend/production/views.py

from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status,filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import logging
import pyodbc
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from .currency_service import CurrencyService
from .models import Musteri, Urun, Siparis, SiparisKalem, SiparisDosya, ULKE_CHOICES
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
    
    @action(detail=False, methods=['post'])
    def mikro_fly_sync(self, request):
        """Mikro Fly V17'den müşteri bilgilerini senkronize et"""
        try:
            sync_result = self._sync_customers_from_mikro_fly()
            return Response(sync_result)
        except Exception as e:
            logging.error(f"Mikro Fly senkronizasyon hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Senkronizasyon hatası: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def sync_status(self, request):
        """Mikro Fly senkronizasyon durumunu getir"""
        try:
            # Son senkronizasyon tarihi
            last_sync_customer = Musteri.objects.filter(
                mikro_fly_sync_tarihi__isnull=False
            ).order_by('-mikro_fly_sync_tarihi').first()
            
            last_sync = last_sync_customer.mikro_fly_sync_tarihi if last_sync_customer else None
            
            # Mikro Fly bağlantısını test et
            is_connected = self._test_mikro_fly_connection()
            
            # İstatistikler
            total_synced = Musteri.objects.filter(mikro_fly_kodu__isnull=False).count()
            total_mikro_customers = self._get_mikro_fly_customer_count() if is_connected else 0
            
            return Response({
                'last_sync': last_sync.isoformat() if last_sync else None,
                'is_connected': is_connected,
                'mikro_fly_version': 'V17',
                'total_customers_in_mikro': total_mikro_customers,
                'total_customers_synced': total_synced
            })
            
        except Exception as e:
            logging.error(f"Sync status hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Durum kontrolü hatası: {str(e)}'
            }, status=500)
    
    def _test_mikro_fly_connection(self):
        """Mikro Fly veritabanı bağlantısını test et"""
        try:
            conn_str = self._get_mikro_fly_connection_string()
            with pyodbc.connect(conn_str, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT TOP 1 1 FROM CARI_HESAPLAR")
                return True
        except Exception as e:
            logging.warning(f"Mikro Fly bağlantı testi başarısız: {str(e)}")
            return False
    
    def _get_mikro_fly_customer_count(self):
        """Mikro Fly'deki toplam müşteri sayısını getir"""
        try:
            conn_str = self._get_mikro_fly_connection_string()
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM CARI_HESAPLAR 
                    WHERE cari_iptal = 0
                """)
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0
    
    def _sync_customers_from_mikro_fly(self):
        """Mikro Fly'den müşteri bilgilerini senkronize et"""
        try:
            conn_str = self._get_mikro_fly_connection_string()
            
            synchronized_count = 0
            updated_count = 0
            new_count = 0
            
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                
                # Mikro Fly'den müşteri bilgilerini çek - gerçek tablo yapısına göre
                cursor.execute("""
                    SELECT 
                        cari_kod,
                        cari_unvan1,
                        cari_CepTel,
                        cari_EMail,
                        cari_unvan2
                    FROM CARI_HESAPLAR 
                    WHERE cari_iptal = 0
                    AND cari_kod IS NOT NULL
                    AND cari_unvan1 IS NOT NULL
                """)
                
                mikro_customers = cursor.fetchall()
                
                for mikro_customer in mikro_customers:
                    mikro_kod, ad, telefon, email, adres = mikro_customer
                    
                    # Mevcut müşteriyi kontrol et
                    existing_customer = Musteri.objects.filter(
                        mikro_fly_kodu=mikro_kod
                    ).first()
                    
                    sync_time = timezone.now()
                    
                    if existing_customer:
                        # Mevcut müşteriyi güncelle
                        existing_customer.ad = ad or existing_customer.ad
                        existing_customer.telefon = telefon or existing_customer.telefon
                        existing_customer.email = email or existing_customer.email
                        existing_customer.adres = adres or existing_customer.adres
                        existing_customer.mikro_fly_sync_tarihi = sync_time
                        existing_customer.aktif = True
                        existing_customer.save()
                        updated_count += 1
                    else:
                        # Yeni müşteri oluştur
                        new_kod = f"MKR{mikro_kod}"  # Mikro Fly prefix'i ekle
                        
                        Musteri.objects.create(
                            kod=new_kod,
                            ad=ad,
                            telefon=telefon or '',
                            email=email or '',
                            adres=adres or '',
                            mikro_fly_kodu=mikro_kod,
                            mikro_fly_sync_tarihi=sync_time,
                            aktif=True,
                            notlar=f"Mikro Fly V17'den senkronize edildi - {sync_time.strftime('%d.%m.%Y %H:%M')}"
                        )
                        new_count += 1
                    
                    synchronized_count += 1
            
            return {
                'status': 'success',
                'synchronized_count': synchronized_count,
                'updated_count': updated_count,
                'new_count': new_count,
                'message': f'{synchronized_count} müşteri senkronize edildi. {new_count} yeni, {updated_count} güncellendi.'
            }
            
        except Exception as e:
            logging.error(f"Mikro Fly senkronizasyon hatası: {str(e)}")
            raise e
    
    def _get_mikro_fly_connection_string(self):
        """Mikro Fly veritabanı bağlantı string'ini oluştur"""
        server = getattr(settings, 'MIKRO_FLY_SERVER', 'localhost')
        database = getattr(settings, 'MIKRO_FLY_DATABASE', 'MikroFly_V17')
        username = getattr(settings, 'MIKRO_FLY_USERNAME', 'sa')
        password = getattr(settings, 'MIKRO_FLY_PASSWORD', '')
        
        # Domain kullanıcısı kontrolü - Windows Authentication kullan
        if '\\' in username:
            return f"""
                DRIVER={{SQL Server}};
                SERVER={server};
                DATABASE={database};
                Trusted_Connection=yes;
            """
        else:
            return f"""
                DRIVER={{SQL Server}};
                SERVER={server};
                DATABASE={database};
                UID={username};
                PWD={password};
                Trusted_Connection=no;
            """

class UrunViewSet(viewsets.ModelViewSet):
    """
    Ürün CRUD işlemleri için ViewSet
    """
    queryset = Urun.objects.all()
    serializer_class = UrunSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['kategori', 'birim']
    search_fields = ['ad', 'kod']
    ordering_fields = ['ad', 'kod', 'stok_miktari']
    ordering = ['ad']
    
    @action(detail=False, methods=['get'])
    def stok_kritik(self, request):
        """Kritik stok seviyesindeki ürünleri getir"""
        kritik = self.queryset.filter(stok_miktari__lte=models.F('minimum_stok'))
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
                urun.stok_miktari += miktar
                urun.save()
                return Response({
                    'status': 'success',
                    'yeni_stok': urun.stok_miktari,
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
    
    @action(detail=False, methods=['post'])
    def mikro_fly_sync(self, request):
        """Mikro Fly V17'den ürün bilgilerini senkronize et"""
        try:
            sync_result = self._sync_products_from_mikro_fly()
            return Response(sync_result)
        except Exception as e:
            logging.error(f"Mikro Fly ürün senkronizasyon hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Ürün senkronizasyon hatası: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def product_sync_status(self, request):
        """Mikro Fly ürün senkronizasyon durumunu getir"""
        try:
            # Son senkronizasyon tarihi
            last_sync_product = Urun.objects.filter(
                mikro_fly_sync_tarihi__isnull=False
            ).order_by('-mikro_fly_sync_tarihi').first()
            
            last_sync = last_sync_product.mikro_fly_sync_tarihi if last_sync_product else None
            
            # Mikro Fly bağlantısını test et
            is_connected = self._test_mikro_fly_connection()
            
            # İstatistikler
            total_synced = Urun.objects.filter(mikro_fly_kodu__isnull=False).count()
            total_mikro_products = self._get_mikro_fly_product_count() if is_connected else 0
            
            return Response({
                'last_sync': last_sync.isoformat() if last_sync else None,
                'is_connected': is_connected,
                'mikro_fly_version': 'V17',
                'total_products_in_mikro': total_mikro_products,
                'total_products_synced': total_synced
            })
            
        except Exception as e:
            logging.error(f"Ürün sync status hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Durum kontrolü hatası: {str(e)}'
            }, status=500)
    
    def _sync_products_from_mikro_fly(self):
        """Mikro Fly'den ürün bilgilerini senkronize et"""
        try:
            conn_str = self._get_mikro_fly_connection_string()
            
            synchronized_count = 0
            updated_count = 0
            new_count = 0
            
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                
                # Mikro Fly'den STOKLAR tablosundan ürün bilgilerini çek
                cursor.execute("""
                    SELECT 
                        sto_kod,
                        sto_isim,
                        sto_birim1_ad,
                        sto_min_stok,
                        sto_pasif_fl,
                        sto_cins
                    FROM STOKLAR 
                    WHERE sto_iptal = 0
                    AND sto_kod IS NOT NULL
                    AND sto_isim IS NOT NULL
                    AND sto_pasif_fl = 0
                """)
                
                mikro_products = cursor.fetchall()
                
                for mikro_product in mikro_products:
                    mikro_kod, ad, birim_ad, min_stok, pasif_fl, cins = mikro_product
                    
                    # Mevcut ürünü kontrol et
                    existing_product = Urun.objects.filter(
                        mikro_fly_kodu=mikro_kod
                    ).first()
                    
                    sync_time = timezone.now()
                    
                    # Mikro Fly birim adını bizim birim seçeneklerimizle eşleştir
                    birim = self._map_mikro_fly_birim(birim_ad or 'adet')
                    
                    # Mikro Fly cins'e göre kategori belirle
                    kategori = self._map_mikro_fly_kategori(cins)
                    
                    if existing_product:
                        # Mevcut ürünü güncelle
                        existing_product.ad = ad or existing_product.ad
                        existing_product.birim = birim
                        existing_product.minimum_stok = int(min_stok or 0)
                        existing_product.kategori = kategori
                        existing_product.mikro_fly_sync_tarihi = sync_time
                        existing_product.save()
                        updated_count += 1
                    else:
                        # Yeni ürün oluştur
                        new_kod = f"MKR{mikro_kod}"  # Mikro Fly prefix'i ekle
                        
                        Urun.objects.create(
                            kod=new_kod,
                            ad=ad,
                            birim=birim,
                            kategori=kategori,
                            minimum_stok=int(min_stok or 0),
                            stok_miktari=0,  # Başlangıç stoku 0
                            mikro_fly_kodu=mikro_kod,
                            mikro_fly_sync_tarihi=sync_time
                        )
                        new_count += 1
                    
                    synchronized_count += 1
            
            return {
                'status': 'success',
                'synchronized_count': synchronized_count,
                'updated_count': updated_count,
                'new_count': new_count,
                'message': f'{synchronized_count} ürün senkronize edildi. {new_count} yeni, {updated_count} güncellendi.'
            }
            
        except Exception as e:
            logging.error(f"Mikro Fly ürün senkronizasyon hatası: {str(e)}")
            raise e
    
    def _get_mikro_fly_product_count(self):
        """Mikro Fly'deki toplam ürün sayısını getir"""
        try:
            conn_str = self._get_mikro_fly_connection_string()
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM STOKLAR 
                    WHERE sto_iptal = 0 AND sto_pasif_fl = 0
                """)
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0
    
    def _map_mikro_fly_birim(self, mikro_birim):
        """Mikro Fly birim adını bizim birim seçeneklerimizle eşleştir"""
        birim_mapping = {
            'AD': 'adet',
            'ADET': 'adet',
            'KG': 'kg',
            'GR': 'gr',
            'LT': 'lt',
            'M': 'm',
            'M2': 'm2',
            'M3': 'm3',
            'CM': 'cm',
            'MM': 'mm',
            'PAKET': 'paket',
            'KOLI': 'koli',
            'KUTU': 'kutu',
            'TORBA': 'torba',
        }
        return birim_mapping.get(mikro_birim.upper() if mikro_birim else '', 'adet')
    
    def _map_mikro_fly_kategori(self, mikro_cins):
        """Mikro Fly cins'e göre kategori belirle"""
        if mikro_cins == 0:  # Hammadde
            return 'hammadde'
        elif mikro_cins == 1:  # Ara ürün
            return 'ara_urun'
        else:  # Bitmiş ürün
            return 'bitmis_urun'
    
    def _test_mikro_fly_connection(self):
        """Mikro Fly veritabanı bağlantısını test et"""
        try:
            conn_str = self._get_mikro_fly_connection_string()
            with pyodbc.connect(conn_str, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT TOP 1 1 FROM STOKLAR")
                return True
        except Exception as e:
            logging.warning(f"Mikro Fly bağlantı testi başarısız: {str(e)}")
            return False
    
    def _get_mikro_fly_connection_string(self):
        """Mikro Fly veritabanı bağlantı string'ini oluştur"""
        server = getattr(settings, 'MIKRO_FLY_SERVER', 'localhost')
        database = getattr(settings, 'MIKRO_FLY_DATABASE', 'MikroFly_V17')
        username = getattr(settings, 'MIKRO_FLY_USERNAME', 'sa')
        password = getattr(settings, 'MIKRO_FLY_PASSWORD', '')
        
        # Domain kullanıcısı kontrolü - Windows Authentication kullan
        if '\\' in username:
            return f"""
                DRIVER={{SQL Server}};
                SERVER={server};
                DATABASE={database};
                Trusted_Connection=yes;
            """
        else:
            return f"""
                DRIVER={{SQL Server}};
                SERVER={server};
                DATABASE={database};
                UID={username};
                PWD={password};
                Trusted_Connection=no;
            """

class SiparisViewSet(viewsets.ModelViewSet):
    queryset = Siparis.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['siparis_no', 'musteri__ad']
    filterset_fields = ['durum', 'musteri', 'tarih']
    ordering_fields = ['tarih', 'teslim_tarihi', 'siparis_no']
    ordering = ['-tarih']
    
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
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

@api_view(['GET'])
def ulke_listesi(request):
    """Ülke listesini döndür"""
    ulkeler = [{"kod": kod, "ad": ad} for kod, ad in ULKE_CHOICES]
    return Response(ulkeler)

# Kur API'leri
@api_view(['GET'])
def exchange_rates(request):
    """
    Güncel döviz kurlarını döndür
    """
    base_currency = request.GET.get('base', 'USD')
    
    try:
        rates_data = CurrencyService.get_exchange_rates(base_currency)
        return Response({
            'success': True,
            'base': rates_data.get('base'),
            'source': rates_data.get('source'),
            'rates': rates_data.get('rates'),
            'timestamp': rates_data.get('timestamp')
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def convert_currency(request):
    """
    Para birimi dönüşümü yap
    
    POST data:
    {
        "amount": "100.50",
        "from_currency": "EUR",
        "to_currency": "USD"  // İsteğe bağlı, varsayılan USD
    }
    """
    try:
        amount = Decimal(str(request.data.get('amount', '0')))
        from_currency = request.data.get('from_currency', 'USD').upper()
        to_currency = request.data.get('to_currency', 'USD').upper()
        
        if to_currency != 'USD':
            return Response({
                'success': False,
                'error': 'Currently only conversion to USD is supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = CurrencyService.convert_to_usd(amount, from_currency)
        
        return Response({
            'success': True,
            'data': {
                'original_amount': str(amount),
                'original_currency': from_currency,
                'converted_amount': str(result['usd_amount']),
                'converted_currency': 'USD',
                'exchange_rate': str(result['rate']),
                'source': result['source']
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def currency_list(request):
    """
    Desteklenen para birimlerini döndür
    """
    currencies = [
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
        {'code': 'TRY', 'name': 'Turkish Lira', 'symbol': '₺'},
        {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
        {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
        {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$'},
        {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},
    ]
    
    return Response({
        'success': True,
        'data': currencies
    })