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
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    # pyodbc not available (production environment)
    pyodbc = None
    PYODBC_AVAILABLE = False
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from .currency_service import CurrencyService
from .models import (
    Musteri, Urun, Siparis, SiparisKalem, SiparisDosya, ULKE_CHOICES,
    IsIstasyonu, StandardIsAdimi, IsAkisi, IsEmri, UrunRecete, IsAkisiOperasyon, BOMTemplate
)
from .serializers import (
    MusteriSerializer, UrunSerializer, 
    SiparisSerializer, SiparisCreateSerializer,
    SiparisKalemSerializer, SiparisDosyaSerializer,
    IsIstasyonuSerializer, StandardIsAdimiSerializer,
    IsAkisiSerializer, IsEmriSerializer, UrunReceteSerializer, BOMTemplateSerializer
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
        if not PYODBC_AVAILABLE:
            logging.warning("pyodbc not available - skipping MikroFly connection test")
            return False
            
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
def istasyon_listesi(request):
    """
    İstasyon listesi - Basit API
    """
    try:
        from .models import IsIstasyonu
        from .serializers import IsIstasyonuSerializer
        
        stations = IsIstasyonu.objects.all()
        serializer = IsIstasyonuSerializer(stations, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

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
def stations_real_data(request):
    """
    Gerçek istasyon verileri - Django admin'deki verilerle aynı
    """
    try:
        from .models import IsIstasyonu
        stations = IsIstasyonu.objects.all()
        
        station_data = []
        for station in stations:
            station_data.append({
                'id': station.id,
                'ad': station.ad,
                'kod': station.kod,
                'tip': station.tip,
                'durum': station.durum,
                'tip_display': station.get_tip_display(),
                'durum_display': station.get_durum_display(),
                'utilization': 60 + (station.id * 7) % 35  # Station ID'ye göre sabit ama farklı değerler
            })
            
        return Response({
            'totalStations': len(station_data),
            'capacityData': station_data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

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

# Production API Views
@api_view(['GET'])
def production_bom_stats(request):
    """
    BOM (Bill of Materials) istatistiklerini döndür
    """
    try:
        # Bitmiş ürünlerin BOM istatistikleri
        products = Urun.objects.filter(kategori='bitmis_urun')
        total_bom = products.count()
        
        # Son güncellenen BOM'ları getir
        recent_bom = []
        for product in products[:10]:  # Son 10 ürün
            # UrunRecete'den component sayısını al
            components_count = UrunRecete.objects.filter(ana_urun=product).count()
            
            recent_bom.append({
                'id': product.id,
                'name': f"{product.ad} Reçetesi",
                'components': components_count,
                'type': 'Bitmiş Ürün',
                'updated': product.guncellenme_tarihi.isoformat() if product.guncellenme_tarihi else product.olusturulma_tarihi.isoformat()
            })
        
        return Response({
            'success': True,
            'data': {
                'totalBOM': total_bom,
                'recentBOM': recent_bom
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def production_mrp_stats(request):
    """
    MRP (Material Requirements Planning) istatistiklerini döndür
    """
    try:
        # Sipariş durumlarına göre istatistikler
        siparisler = Siparis.objects.all()
        
        # Durum bazlı sayımlar
        planned_orders = siparisler.filter(durum='beklemede').count()
        waiting_materials = siparisler.filter(durum='malzeme_planlandi').count()
        ready_orders = siparisler.filter(durum='is_emirleri_olusturuldu').count()
        in_production = siparisler.filter(durum='uretimde').count()
        completed = siparisler.filter(durum='tamamlandi').count()
        
        # Bu aylık tamamlanan siparişler
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_completed = siparisler.filter(
            durum='tamamlandi',
            guncellenme_tarihi__gte=current_month
        ).count()
        
        # Gecikmiş siparişler (tahmini - gelecekte kalemlerden hesaplanacak)
        delayed_orders = siparisler.filter(
            durum__in=['uretimde', 'is_emirleri_olusturuldu'],
            tarih__lt=timezone.now().date()
        ).count()
        
        # Kritik malzemeler (örnek veri - gelecekte gerçek hesaplama yapılacak)
        critical_materials = [
            {'name': 'Çelik Sac', 'shortage': 500, 'unit': 'kg'},
            {'name': 'Bakır Tel', 'shortage': 200, 'unit': 'metre'},
            {'name': 'Transformer Oil', 'shortage': 150, 'unit': 'litre'}
        ]
        
        return Response({
            'success': True,
            'data': {
                'plannedOrders': planned_orders,
                'waitingMaterials': waiting_materials,
                'readyOrders': ready_orders,
                'inProduction': in_production,
                'completed': completed,
                'monthlyCompleted': monthly_completed,
                'delayedOrders': delayed_orders,
                'avgDeliveryTime': 14.5,  # Gelecekte gerçek hesaplama
                'criticalMaterials': critical_materials
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def istasyonlar_direct(request):
    """
    İstasyon listesi - direct API
    """
    try:
        from .models import IsIstasyonu
        stations = IsIstasyonu.objects.all()
        
        station_list = []
        for station in stations:
            station_list.append({
                'id': station.id,
                'ad': station.ad,
                'kod': station.kod,
                'tip': station.tip,
                'durum': station.durum,
                'tip_display': station.get_tip_display(),
                'durum_display': station.get_durum_display()
            })
            
        return Response(station_list)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def production_station_stats(request):
    """
    İş istasyonu istatistiklerini döndür
    """
    try:
        # İş istasyonlarının sayısı
        total_stations = IsIstasyonu.objects.count()
        
        # Gerçek istasyon verilerini çek
        stations = IsIstasyonu.objects.all()[:10]  # İlk 10 istasyon
        capacity_data = []
        
        for station in stations:
            # Gerçek istasyon bilgileriyle kapasite verisi oluştur
            import random
            utilization = random.randint(60, 95)
            
            capacity_data.append({
                'id': station.id,
                'name': station.ad,  # Gerçek istasyon adı
                'code': station.kod,  # İstasyon kodu
                'type': station.get_tip_display(),  # İstasyon tipi (display value)
                'status': station.get_durum_display(),  # Durum (display value)
                'utilization': utilization,
                'daily_hours': float(station.gunluk_calisma_saati),
                'hourly_cost': float(station.saatlik_maliyet),
                'required_operators': station.gerekli_operator_sayisi,
                'location': station.lokasyon or '',
                'description': station.aciklama or ''
            })
        
        # Eğer istasyon yoksa örnek veri
        if not capacity_data:
            capacity_data = [
                {'name': 'Kesim', 'utilization': 85},
                {'name': 'Sargı', 'utilization': 92},
                {'name': 'Montaj', 'utilization': 78},
                {'name': 'Test', 'utilization': 65},
                {'name': 'Boya', 'utilization': 88},
                {'name': 'Paketleme', 'utilization': 72}
            ]
        
        return Response({
            'success': True,
            'data': {
                'totalStations': total_stations,
                'capacityData': capacity_data
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def production_operations_stats(request):
    """
    Üretim operasyon istatistiklerini döndür
    """
    try:
        # Standard iş adımlarının sayısı
        total_operations = StandardIsAdimi.objects.count()
        
        return Response({
            'success': True,
            'data': {
                'totalOperations': total_operations
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Production ViewSets

class IsIstasyonuViewSet(viewsets.ModelViewSet):
    """İş İstasyonu CRUD işlemleri"""
    queryset = IsIstasyonu.objects.all()
    serializer_class = IsIstasyonuSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['durum', 'tip']
    search_fields = ['ad', 'kod', 'lokasyon']
    ordering_fields = ['ad', 'kod', 'gunluk_calisma_saati']
    ordering = ['ad']
    
    def destroy(self, request, *args, **kwargs):
        """İstasyon silme - İlişkili kayıtları kontrol et"""
        from django.db import models
        
        instance = self.get_object()
        
        # İlişkili operasyonları kontrol et
        related_operations = instance.isakisioperasyon_set.count()
        
        if related_operations > 0:
            return Response({
                'error': 'Bu istasyon silinemez',
                'detail': f'Bu istasyon {related_operations} adet iş akışı operasyonunda kullanılıyor. Önce ilgili iş akışlarını düzenleyin.',
                'related_count': related_operations
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # İlişki yoksa normal silme işlemi
        return super().destroy(request, *args, **kwargs)


class StandardIsAdimiViewSet(viewsets.ModelViewSet):
    """Standard İş Adımı CRUD işlemleri"""
    queryset = StandardIsAdimi.objects.all()
    serializer_class = StandardIsAdimiSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['kategori', 'aktif']
    search_fields = ['ad', 'aciklama']
    ordering_fields = ['ad', 'kategori', 'standart_sure']
    ordering = ['kategori', 'ad']


class IsAkisiViewSet(viewsets.ModelViewSet):
    """İş Akışı CRUD işlemleri"""
    queryset = IsAkisi.objects.all()
    serializer_class = IsAkisiSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['aktif', 'urun', 'tip']
    search_fields = ['ad', 'kod', 'urun__ad']
    ordering_fields = ['ad', 'kod', 'olusturulma_tarihi']
    ordering = ['ad']


class IsEmriViewSet(viewsets.ModelViewSet):
    """İş Emri CRUD işlemleri"""
    queryset = IsEmri.objects.all()
    serializer_class = IsEmriSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['durum', 'istasyon', 'siparis', 'urun']
    search_fields = ['is_emri_no', 'siparis__siparis_no', 'urun__ad']
    ordering_fields = ['is_emri_no', 'baslangic_tarihi', 'bitis_tarihi']
    ordering = ['-baslangic_tarihi']


class UrunReceteViewSet(viewsets.ModelViewSet):
    """Ürün Reçetesi (BOM) CRUD işlemleri"""
    serializer_class = UrunReceteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['urun', 'malzeme', 'malzeme__kategori']
    search_fields = ['urun__ad', 'malzeme__ad', 'malzeme__kod', 'notlar']
    ordering_fields = ['urun__ad', 'malzeme__ad', 'miktar']
    ordering = ['urun__ad', 'malzeme__ad']
    
    def get_queryset(self):
        """Sadece bitmiş ürün ve ara ürünlerin reçetelerini döndür
        Hammaddelerin reçetesi olmaz!"""
        return UrunRecete.objects.filter(
            urun__kategori__in=['bitmis_urun', 'ara_urun']
        ).select_related('urun', 'malzeme')


class BOMTemplateViewSet(viewsets.ModelViewSet):
    """BOM Template CRUD işlemleri"""
    queryset = BOMTemplate.objects.all()
    serializer_class = BOMTemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['eslestirilen_urun']
    search_fields = ['bom_tanimi', 'aciklama']
    ordering_fields = ['bom_tanimi', 'guncellenme_tarihi']
    ordering = ['-guncellenme_tarihi']
    
    def perform_create(self, serializer):
        """BOM Template olusturma islemini debug et"""
        import logging
        
        # Logger kullan - encoding problemini önler
        logger = logging.getLogger('django')
        
        logger.info("=== BOM Template Creation Debug ===")
        
        # Request data'yı safe log et
        try:
            bom_tanimi = self.request.data.get('bom_tanimi', 'N/A')
            eslestirilen_urun_id = self.request.data.get('eslestirilen_urun', 'None')
            malzemeler_count = len(self.request.data.get('malzemeler', []))
            
            logger.info(f"BOM Name: {bom_tanimi}")
            logger.info(f"Product ID: {eslestirilen_urun_id}")
            logger.info(f"Materials count: {malzemeler_count}")
            
        except Exception as e:
            logger.error(f"Request data debug error: {e}")
        
        # Validated data kontrol et
        try:
            eslestirilen_urun = serializer.validated_data.get('eslestirilen_urun')
            logger.info(f"Validated product object: {eslestirilen_urun is not None}")
            logger.info(f"Product type: {type(eslestirilen_urun)}")
            
            if eslestirilen_urun:
                logger.info(f"Product ID: {eslestirilen_urun.id}")
                
        except Exception as e:
            logger.error(f"Validated data debug error: {e}")
        
        # Normal kaydetme işlemini yap
        try:
            instance = serializer.save()
            logger.info(f"SUCCESS: Created BOM Template ID: {instance.id}")
            logger.info(f"SUCCESS: eslestirilen_urun saved: {instance.eslestirilen_urun is not None}")
            
            if instance.eslestirilen_urun:
                logger.info(f"SUCCESS: Product ID in DB: {instance.eslestirilen_urun.id}")
            
        except Exception as e:
            logger.error(f"Save error: {e}")
            raise
            
        logger.info("=== End Debug ===")
        return instance