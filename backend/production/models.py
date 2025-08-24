# backend/production/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User

# Ülke seçenekleri
ULKE_CHOICES = [
    ('AF', 'Afganistan'),
    ('AL', 'Arnavutluk'),
    ('DZ', 'Cezayir'),
    ('AS', 'Amerikan Samoası'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AQ', 'Antarktika'),
    ('AG', 'Antigua ve Barbuda'),
    ('AR', 'Arjantin'),
    ('AM', 'Ermenistan'),
    ('AW', 'Aruba'),
    ('AU', 'Avustralya'),
    ('AT', 'Avusturya'),
    ('AZ', 'Azerbaycan'),
    ('BS', 'Bahamalar'),
    ('BH', 'Bahreyn'),
    ('BD', 'Bangladeş'),
    ('BB', 'Barbados'),
    ('BY', 'Belarus'),
    ('BE', 'Belçika'),
    ('BZ', 'Belize'),
    ('BJ', 'Benin'),
    ('BM', 'Bermuda'),
    ('BT', 'Butan'),
    ('BO', 'Bolivya'),
    ('BA', 'Bosna Hersek'),
    ('BW', 'Botsvana'),
    ('BR', 'Brezilya'),
    ('BG', 'Bulgaristan'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Kamboçya'),
    ('CM', 'Kamerun'),
    ('CA', 'Kanada'),
    ('CV', 'Cape Verde'),
    ('KY', 'Cayman Adaları'),
    ('CF', 'Orta Afrika Cumhuriyeti'),
    ('TD', 'Çad'),
    ('CL', 'Şili'),
    ('CN', 'Çin'),
    ('CO', 'Kolombiya'),
    ('KM', 'Komorlar'),
    ('CG', 'Kongo'),
    ('CD', 'Demokratik Kongo Cumhuriyeti'),
    ('CR', 'Kosta Rika'),
    ('CI', 'Fildişi Sahili'),
    ('HR', 'Hırvatistan'),
    ('CU', 'Küba'),
    ('CY', 'Kıbrıs'),
    ('CZ', 'Çek Cumhuriyeti'),
    ('DK', 'Danimarka'),
    ('DJ', 'Cibuti'),
    ('DM', 'Dominika'),
    ('DO', 'Dominik Cumhuriyeti'),
    ('EC', 'Ekvador'),
    ('EG', 'Mısır'),
    ('SV', 'El Salvador'),
    ('GQ', 'Ekvator Ginesi'),
    ('ER', 'Eritre'),
    ('EE', 'Estonya'),
    ('ET', 'Etiyopya'),
    ('FK', 'Falkland Adaları'),
    ('FO', 'Faroe Adaları'),
    ('FJ', 'Fiji'),
    ('FI', 'Finlandiya'),
    ('FR', 'Fransa'),
    ('GA', 'Gabon'),
    ('GM', 'Gambiya'),
    ('GE', 'Gürcistan'),
    ('DE', 'Almanya'),
    ('GH', 'Gana'),
    ('GI', 'Cebelitarık'),
    ('GR', 'Yunanistan'),
    ('GL', 'Grönland'),
    ('GD', 'Grenada'),
    ('GU', 'Guam'),
    ('GT', 'Guatemala'),
    ('GG', 'Guernsey'),
    ('GN', 'Gine'),
    ('GW', 'Gine-Bissau'),
    ('GY', 'Guyana'),
    ('HT', 'Haiti'),
    ('HN', 'Honduras'),
    ('HK', 'Hong Kong'),
    ('HU', 'Macaristan'),
    ('IS', 'İzlanda'),
    ('IN', 'Hindistan'),
    ('ID', 'Endonezya'),
    ('IR', 'İran'),
    ('IQ', 'Irak'),
    ('IE', 'İrlanda'),
    ('IM', 'Man Adası'),
    ('IL', 'İsrail'),
    ('IT', 'İtalya'),
    ('JM', 'Jamaika'),
    ('JP', 'Japonya'),
    ('JE', 'Jersey'),
    ('JO', 'Ürdün'),
    ('KZ', 'Kazakistan'),
    ('KE', 'Kenya'),
    ('KI', 'Kiribati'),
    ('KP', 'Kuzey Kore'),
    ('KR', 'Güney Kore'),
    ('KW', 'Kuveyt'),
    ('KG', 'Kırgızistan'),
    ('LA', 'Laos'),
    ('LV', 'Letonya'),
    ('LB', 'Lübnan'),
    ('LS', 'Lesotho'),
    ('LR', 'Liberya'),
    ('LY', 'Libya'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Litvanya'),
    ('LU', 'Lüksemburg'),
    ('MO', 'Makao'),
    ('MK', 'Makedonya'),
    ('MG', 'Madagaskar'),
    ('MW', 'Malavi'),
    ('MY', 'Malezya'),
    ('MV', 'Maldivler'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MH', 'Marshall Adaları'),
    ('MR', 'Moritanya'),
    ('MU', 'Mauritius'),
    ('MX', 'Meksika'),
    ('FM', 'Mikronezya'),
    ('MD', 'Moldova'),
    ('MC', 'Monako'),
    ('MN', 'Moğolistan'),
    ('ME', 'Karadağ'),
    ('MA', 'Fas'),
    ('MZ', 'Mozambik'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibya'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NL', 'Hollanda'),
    ('NC', 'Yeni Kaledonya'),
    ('NZ', 'Yeni Zelanda'),
    ('NI', 'Nikaragua'),
    ('NE', 'Nijer'),
    ('NG', 'Nijerya'),
    ('NO', 'Norveç'),
    ('OM', 'Umman'),
    ('PK', 'Pakistan'),
    ('PW', 'Palau'),
    ('PS', 'Filistin'),
    ('PA', 'Panama'),
    ('PG', 'Papua Yeni Gine'),
    ('PY', 'Paraguay'),
    ('PE', 'Peru'),
    ('PH', 'Filipinler'),
    ('PL', 'Polonya'),
    ('PT', 'Portekiz'),
    ('PR', 'Porto Riko'),
    ('QA', 'Katar'),
    ('RO', 'Romanya'),
    ('RU', 'Rusya'),
    ('RW', 'Ruanda'),
    ('KN', 'Saint Kitts ve Nevis'),
    ('LC', 'Saint Lucia'),
    ('VC', 'Saint Vincent ve Grenadinler'),
    ('WS', 'Samoa'),
    ('SM', 'San Marino'),
    ('ST', 'Sao Tome ve Principe'),
    ('SA', 'Suudi Arabistan'),
    ('SN', 'Senegal'),
    ('RS', 'Sırbistan'),
    ('SC', 'Seyşeller'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapur'),
    ('SK', 'Slovakya'),
    ('SI', 'Slovenya'),
    ('SB', 'Solomon Adaları'),
    ('SO', 'Somali'),
    ('ZA', 'Güney Afrika'),
    ('SS', 'Güney Sudan'),
    ('ES', 'İspanya'),
    ('LK', 'Sri Lanka'),
    ('SD', 'Sudan'),
    ('SR', 'Surinam'),
    ('SZ', 'Svaziland'),
    ('SE', 'İsveç'),
    ('CH', 'İsviçre'),
    ('SY', 'Suriye'),
    ('TW', 'Tayvan'),
    ('TJ', 'Tacikistan'),
    ('TZ', 'Tanzanya'),
    ('TH', 'Tayland'),
    ('TL', 'Doğu Timor'),
    ('TG', 'Togo'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad ve Tobago'),
    ('TN', 'Tunus'),
    ('TR', 'Türkiye'),
    ('TM', 'Türkmenistan'),
    ('TV', 'Tuvalu'),
    ('UG', 'Uganda'),
    ('UA', 'Ukrayna'),
    ('AE', 'Birleşik Arap Emirlikleri'),
    ('GB', 'Birleşik Krallık'),
    ('US', 'Amerika Birleşik Devletleri'),
    ('UY', 'Uruguay'),
    ('UZ', 'Özbekistan'),
    ('VU', 'Vanuatu'),
    ('VE', 'Venezuela'),
    ('VN', 'Vietnam'),
    ('VG', 'Virjin Adaları (İngiliz)'),
    ('VI', 'Virjin Adaları (ABD)'),
    ('WF', 'Wallis ve Futuna'),
    ('EH', 'Batı Sahara'),
    ('YE', 'Yemen'),
    ('ZM', 'Zambiya'),
    ('ZW', 'Zimbabve'),
]

class Musteri(models.Model):
    """Müşteri bilgileri modeli"""
    
    # Temel bilgiler
    ad = models.CharField(max_length=200, verbose_name="Müşteri Adı")
    kod = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Müşteri Kodu",
        help_text="Örnek: MST001"
    )
    
    # İletişim bilgileri
    telefon_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon numarası '+999999999' formatında olmalıdır."
    )
    telefon = models.CharField(
        validators=[telefon_regex], 
        max_length=17, 
        blank=True,
        verbose_name="Telefon"
    )
    email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="E-posta"
    )
    adres = models.TextField(
        blank=True,
        verbose_name="Adres"
    )
    ulke = models.CharField(
        max_length=2,
        choices=ULKE_CHOICES,
        default='TR',
        verbose_name="Ülke"
    )
    
    # Ek bilgiler
    notlar = models.TextField(
        blank=True,
        verbose_name="Notlar"
    )
    aktif = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    # Mikro Fly Entegrasyonu
    mikro_fly_kodu = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Mikro Fly Müşteri Kodu",
        help_text="Mikro Fly V17'deki müşteri kodu"
    )
    mikro_fly_sync_tarihi = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Son Senkronizasyon Tarihi",
        help_text="Mikro Fly'den son senkronizasyon tarihi"
    )
    
    # Zaman damgaları
    olusturulma_tarihi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    guncellenme_tarihi = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )
    
    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"
        ordering = ['ad']
    
    def __str__(self):
        return f"{self.kod} - {self.ad}"

class Urun(models.Model):
    
    KATEGORI_CHOICES = [
        ('hammadde', 'Hammadde'),
        ('ara_urun', 'Ara Ürün'),
        ('bitmis_urun', 'Bitmiş Ürün'),
    ]
    BIRIM_CHOICES = [
        # Uzunluk birimleri
        ('mm', 'Milimetre (mm)'),
        ('cm', 'Santimetre (cm)'),
        ('m', 'Metre (m)'),
        ('m2', 'Metrekare (m²)'),
        ('m3', 'Metreküp (m³)'),
        
        # Ağırlık birimleri
        ('mg', 'Miligram (mg)'),
        ('gr', 'Gram (gr)'),
        ('kg', 'Kilogram (kg)'),
        ('ton', 'Ton'),
        
        # Hacim birimleri
        ('ml', 'Mililitre (ml)'),
        ('lt', 'Litre (lt)'),
        
        # Adet birimleri
        ('adet', 'Adet'),
        ('paket', 'Paket'),
        ('koli', 'Koli'),
        ('deste', 'Deste'),
        ('düzine', 'Düzine'),
        ('kutu', 'Kutu'),
        ('torba', 'Torba'),
        ('rulo', 'Rulo'),
        ('top', 'Top'),
        ('levha', 'Levha'),
        ('tabaka', 'Tabaka'),
        ('çift', 'Çift'),
        ('takım', 'Takım'),
        ('set', 'Set'),
    ]
    
    ad = models.CharField(max_length=200)
    kod = models.CharField(max_length=50, unique=True)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='bitmis_urun')
    birim = models.CharField(max_length=20, choices=BIRIM_CHOICES, default='adet') 
    stok_miktari = models.IntegerField(default=0)
    minimum_stok = models.IntegerField(default=0)
    
    # Mikro Fly Entegrasyonu
    mikro_fly_kodu = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Mikro Fly Stok Kodu",
        help_text="Mikro Fly V17'deki stok kodu"
    )
    mikro_fly_sync_tarihi = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Son Senkronizasyon Tarihi",
        help_text="Mikro Fly'den son senkronizasyon tarihi"
    )
    
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['kategori', 'ad']
    
    def __str__(self):
        return f"{self.ad} ({self.get_kategori_display()})"
    
    @property
    def stok_durumu(self):
        """Stok durumunu kontrol et"""
        if self.stok_miktari <= 0:
            return "Stok Yok"
        elif self.stok_miktari <= self.minimum_stok:
            return "Kritik Stok"
        else:
            return "Stok Var"
        
class UrunRecete(models.Model):
    """Ürün reçetesi - hangi üründen ne kadar kullanılacağını belirtir"""
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='recete')
    malzeme = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='kullanildigi_urunler')
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    notlar = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Ürün Reçetesi'
        verbose_name_plural = 'Ürün Reçeteleri'
        unique_together = ['urun', 'malzeme']  # Aynı ürün-malzeme çifti tekrar edilemez
    
    def __str__(self):
        return f"{self.urun.ad} için {self.miktar} {self.malzeme.birim} {self.malzeme.ad}"
    
    def clean(self):
        """Validasyon: Bir ürün kendisini malzeme olarak kullanamaz"""
        from django.core.exceptions import ValidationError
        if self.urun == self.malzeme:
            raise ValidationError('Bir ürün kendisini malzeme olarak kullanamaz!')
        
class Siparis(models.Model):
    DURUM_CHOICES = [
        ('beklemede', 'Beklemede'),
        ('malzeme_planlandi', 'Malzeme Planlaması Yapıldı'),
        ('is_emirleri_olusturuldu', 'İş Emirleri Oluşturuldu'),
        ('uretimde', 'Üretimde'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal Edildi'),
    ]
    
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE, related_name='siparisler')
    siparis_no = models.CharField(max_length=50, unique=True)
    tarih = models.DateField(default=timezone.now)
    durum = models.CharField(max_length=25, choices=DURUM_CHOICES, default='beklemede')
    
    # Ülke bilgileri
    musteri_ulke = models.CharField(
        max_length=2,
        choices=ULKE_CHOICES,
        blank=True,
        verbose_name="Müşteri Ülke",
        help_text="Müşteri adresinden otomatik alınır"
    )
    son_kullanici_ulke = models.CharField(
        max_length=2,
        choices=ULKE_CHOICES,
        default='TR',
        verbose_name="Son Kullanıcı Ülke",
        help_text="Varsayılan olarak müşteri ülkesi ile aynıdır"
    )
    
    notlar = models.TextField(blank=True)
    
    # Dosya alanları
    siparis_mektubu = models.FileField(
        upload_to='siparis_dosyalari/mektuplar/%Y/%m/', 
        blank=True, 
        null=True,
        verbose_name='Sipariş Mektubu',
        help_text='Sipariş mektubunu yükleyiniz (Zorunlu - PDF, DOC, DOCX)'
    )
    maliyet_hesabi = models.FileField(
        upload_to='siparis_dosyalari/maliyet/%Y/%m/', 
        blank=True, 
        null=True,
        verbose_name='Maliyet Hesap Tablosu',
        help_text='Maliyet hesap tablosunu yükleyiniz (Zorunlu - Excel, PDF)'
    )
    dosya = models.FileField(                    
        upload_to='siparis_dosyalari/%Y/%m/', 
        blank=True, 
        null=True,
        verbose_name='Ek Dosya',
        help_text='İsteğe bağlı ek dosya yükleyebilirsiniz'
    )
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        ordering = ['-tarih']
    
    def __str__(self):
        return f"{self.siparis_no} - {self.musteri.ad}"
    
    def toplam_tutar(self):
        """USD cinsinden toplam tutar"""
        return sum(kalem.toplam_fiyat_usd() for kalem in self.kalemler.all())

class SiparisKalem(models.Model):
    DOVIZ_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('TRY', 'Turkish Lira'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
    ]
    
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE, related_name='kalemler')
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    miktar = models.IntegerField()
    
    # Orijinal para birimi ve fiyat
    doviz = models.CharField(
        max_length=3, 
        choices=DOVIZ_CHOICES, 
        default='USD',
        verbose_name="Para Birimi"
    )
    birim_fiyat = models.DecimalField(
        max_digits=15, 
        decimal_places=4,
        verbose_name="Birim Fiyat",
        help_text="Seçilen para birimindeki birim fiyat"
    )
    
    # USD cinsinden değerler (ana döviz)
    kur = models.DecimalField(
        max_digits=10, 
        decimal_places=6,
        default=1.000000,
        verbose_name="Döviz Kuru",
        help_text="1 birim seçilen para birimi = X USD"
    )
    birim_fiyat_usd = models.DecimalField(
        max_digits=15, 
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Birim Fiyat (USD)",
        help_text="USD cinsinden birim fiyat (otomatik hesaplanır)"
    )
    
    teslim_tarihi = models.DateField(
        default=timezone.now,
        verbose_name="Teslim Tarihi",
        help_text="Bu kalemin teslim tarihi"
    )
    son_kullanici_ulke = models.CharField(
        max_length=2, 
        choices=ULKE_CHOICES, 
        default='TR',
        verbose_name="Son Kullanıcı Ülke",
        help_text="Bu kalemin gönderileceği son kullanıcı ülkesi"
    )
    notlar = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Sipariş Kalemi'
        verbose_name_plural = 'Sipariş Kalemleri'
    
    def __str__(self):
        return f"{self.siparis.siparis_no} - {self.urun.ad} ({self.miktar} {self.urun.birim})"
    
    def toplam_fiyat(self):
        """Orijinal para birimindeki toplam fiyat"""
        return self.miktar * self.birim_fiyat
    
    def toplam_fiyat_usd(self):
        """USD cinsinden toplam fiyat"""
        return self.miktar * self.birim_fiyat_usd
    
    def save(self, *args, **kwargs):
        # Birim fiyat USD'yi otomatik hesapla
        if self.doviz == 'USD':
            self.birim_fiyat_usd = self.birim_fiyat
            self.kur = 1.000000
        else:
            # Kur ile USD'ye çevir
            self.birim_fiyat_usd = self.birim_fiyat * self.kur
        
        super().save(*args, **kwargs)
    
class SiparisDosya(models.Model):
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE, related_name='dosyalar')
    dosya = models.FileField(upload_to='siparis_dosyalari/%Y/%m/')
    aciklama = models.CharField(max_length=200, blank=True)
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sipariş Dosyası'
        verbose_name_plural = 'Sipariş Dosyaları'
    
    def __str__(self):
        return f"{self.siparis.siparis_no} - {self.dosya.name}"
    
class MalzemeIhtiyac(models.Model):
    """Malzeme planlama sonucu oluşan ihtiyaç kaydı"""
    
    ISLEM_CHOICES = [
        ('satin_al', 'Satın Al'),
        ('stoktan_kullan', 'Stoktan Kullan'),
    ]
    
    DURUM_CHOICES = [
        ('beklemede', 'Beklemede'),
        ('onaylandi', 'Onaylandı'),
        ('siparis_verildi', 'Sipariş Verildi'),
        ('kismi_geldi', 'Kısmi Geldi'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal'),
    ]
    
    # Temel bilgiler
    malzeme_adi = models.CharField(max_length=200, verbose_name="Malzeme Adı")
    miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    birim = models.CharField(max_length=20, verbose_name="Birim")
    
    # İşlem bilgileri
    islem_tipi = models.CharField(max_length=20, choices=ISLEM_CHOICES, verbose_name="İşlem Tipi")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='beklemede', verbose_name="Durum")
    
    # İlişkili siparişler (JSON olarak saklayacağız)
    ilgili_siparisler = models.JSONField(verbose_name="İlgili Siparişler")
    ilgili_urunler = models.JSONField(verbose_name="İlgili Ürünler")
    
    # Sistem bilgileri
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    notlar = models.TextField(blank=True, verbose_name="Notlar")
    
    class Meta:
        verbose_name = "Malzeme İhtiyacı"
        verbose_name_plural = "Malzeme İhtiyaçları"
        ordering = ['-olusturulma_tarihi']
    
    def __str__(self):
        return f"{self.malzeme_adi} - {self.miktar} {self.birim} ({self.get_islem_tipi_display()})"
    
class Tedarikci(models.Model):
    """Tedarikçi bilgileri"""
    ad = models.CharField(max_length=200, verbose_name="Tedarikçi Adı")
    kod = models.CharField(max_length=20, unique=True, verbose_name="Tedarikçi Kodu")
    telefon = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="E-posta")
    adres = models.TextField(blank=True, verbose_name="Adres")
    vergi_no = models.CharField(max_length=20, blank=True, verbose_name="Vergi No")
    vergi_dairesi = models.CharField(max_length=100, blank=True, verbose_name="Vergi Dairesi")
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        verbose_name = "Tedarikçi"
        verbose_name_plural = "Tedarikçiler"
        ordering = ['ad']
    
    def __str__(self):
        return f"{self.kod} - {self.ad}"

class SatinAlmaSiparisi(models.Model):
    """Satın alma siparişi"""
    
    DURUM_CHOICES = [
        ('bekliyor', 'Bekliyor'),
        ('kismi', 'Kısmi Teslim'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal')
    ]
    
    siparis_no = models.CharField(max_length=50, unique=True, verbose_name="Sipariş No")
    tedarikci = models.ForeignKey(Tedarikci, on_delete=models.PROTECT, verbose_name="Tedarikçi")
    tarih = models.DateField(default=timezone.now, verbose_name="Sipariş Tarihi")
    teslim_tarihi = models.DateField(verbose_name="Teslim Tarihi")
    guncel_teslim_tarihi = models.DateField(verbose_name="Güncel Teslim Tarihi", null=True, blank=True)
    toplam_tutar = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Tutar")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='bekliyor', verbose_name="Durum")
    
    # İlişkili malzeme ihtiyaçları
    malzeme_ihtiyaclari = models.ManyToManyField(MalzemeIhtiyac, through='SatinAlmaKalemi', verbose_name="Malzeme İhtiyaçları")
    
    # Dosyalar
    siparis_dosyasi = models.FileField(upload_to='satinalma_siparisleri/', blank=True, verbose_name="Sipariş Dosyası")
    
    # Sistem bilgileri
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Satın Alma Siparişi"
        verbose_name_plural = "Satın Alma Siparişleri"
        ordering = ['-tarih']
    
    def __str__(self):
        return f"{self.siparis_no} - {self.tedarikci.ad}"
    
    @property
    def toplam_kalem_sayisi(self):
        """Toplam kalem sayısı"""
        return self.kalemler.count()
    
    @property
    def tamamlanan_kalem_sayisi(self):
        """Tam olarak teslim edilmiş kalem sayısı"""
        tamamlanan = 0
        for kalem in self.kalemler.all():
            if kalem.gelen_toplam_miktar >= kalem.miktar:
                tamamlanan += 1
        return tamamlanan
    
    @property
    def bekleyen_kalem_sayisi(self):
        """Hiç gelmemiş kalem sayısı"""
        bekleyen = 0
        for kalem in self.kalemler.all():
            if kalem.gelen_toplam_miktar <= 0:
                bekleyen += 1
        return bekleyen
    
    @property
    def kismi_kalem_sayisi(self):
        """Kısmi gelmiş kalem sayısı"""
        kismi = 0
        for kalem in self.kalemler.all():
            if 0 < kalem.gelen_toplam_miktar < kalem.miktar:
                kismi += 1
        return kismi
    
    @property
    def genel_tamamlanma_yuzdesi(self):
        """Siparişin genel tamamlanma yüzdesi"""
        try:
            toplam_siparis_edilen = 0
            toplam_gelen = 0
            
            for kalem in self.kalemler.all():
                toplam_siparis_edilen += float(kalem.miktar or 0)
                toplam_gelen += kalem.gelen_toplam_miktar
            
            if toplam_siparis_edilen <= 0:
                return 0.0
                
            return min(100.0, (toplam_gelen / toplam_siparis_edilen) * 100)
        except Exception:
            return 0.0
    
    @property
    def siparis_durumu(self):
        """Siparişin genel durumu"""
        if self.toplam_kalem_sayisi == 0:
            return "bos"
        elif self.bekleyen_kalem_sayisi == self.toplam_kalem_sayisi:
            return "bekliyor"
        elif self.tamamlanan_kalem_sayisi == self.toplam_kalem_sayisi:
            return "tamamlandi"
        else:
            return "kismi"

class SatinAlmaKalemi(models.Model):
    """Satın alma sipariş kalemi"""
    siparis = models.ForeignKey(SatinAlmaSiparisi, on_delete=models.CASCADE, related_name='kalemler', verbose_name="Sipariş")
    malzeme_ihtiyaci = models.ForeignKey(MalzemeIhtiyac, on_delete=models.PROTECT, verbose_name="Malzeme İhtiyacı")
    miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat")
    toplam_fiyat = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Fiyat")
    
    class Meta:
        verbose_name = "Satın Alma Kalemi"
        verbose_name_plural = "Satın Alma Kalemleri"
    
    def save(self, *args, **kwargs):
        self.toplam_fiyat = self.miktar * self.birim_fiyat
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.malzeme_ihtiyaci.malzeme_adi} - {self.miktar} {self.malzeme_ihtiyaci.birim} ({self.siparis.siparis_no})"
    
    @property
    def gelen_toplam_miktar(self):
        """Bu kaleme ait toplam gelen miktar"""
        try:
            from django.db.models import Sum
            toplam = self.gelisler.aggregate(
                toplam=Sum('gelen_miktar')
            )['toplam']
            return float(toplam) if toplam is not None else 0.0
        except Exception:
            return 0.0
    
    @property  
    def kalan_miktar(self):
        """Henüz gelmemiş miktar"""
        try:
            miktar = float(self.miktar) if self.miktar is not None else 0.0
            gelen = self.gelen_toplam_miktar
            return max(0.0, miktar - gelen)
        except Exception:
            return 0.0
    
    @property
    def tamamlanma_yuzdesi(self):
        """Tamamlanma yüzdesi (0-100)"""
        try:
            miktar = float(self.miktar) if self.miktar is not None else 0.0
            if miktar <= 0:
                return 0.0
            gelen = self.gelen_toplam_miktar
            return min(100.0, (gelen / miktar) * 100)
        except Exception:
            return 0.0
    
    @property
    def gelis_durumu(self):
        """Geliş durumu: bekliyor, kismi, tam, fazla"""
        try:
            gelen = self.gelen_toplam_miktar
            miktar = float(self.miktar) if self.miktar is not None else 0.0
            
            if gelen <= 0:
                return "bekliyor"
            elif gelen < miktar:
                return "kismi" 
            elif gelen == miktar:
                return "tam"
            else:
                return "fazla"
        except Exception:
            return "bekliyor"
        
class SatinAlmaTeslimGuncelleme(models.Model):
    """Satın alma siparişi teslim tarihi güncellemeleri"""
    siparis = models.ForeignKey(SatinAlmaSiparisi, on_delete=models.CASCADE, related_name='teslim_guncellemeleri', verbose_name="Sipariş")
    eski_teslim_tarihi = models.DateField(verbose_name="Eski Teslim Tarihi")
    yeni_teslim_tarihi = models.DateField(verbose_name="Yeni Teslim Tarihi")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Güncelleyen")
    guncelleme_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Güncelleme Tarihi")
    
    class Meta:
        verbose_name = "Teslim Tarihi Güncellemesi"
        verbose_name_plural = "Teslim Tarihi Güncellemeleri"
        ordering = ['-guncelleme_tarihi']
    
    def __str__(self):
        return f"{self.siparis.siparis_no} - {self.yeni_teslim_tarihi}"

class MalzemeGelis(models.Model):
    """Satın alma siparişlerine karşı gelen malzeme kayıtları"""
    
    # İlişkiler
    satis_siparisi = models.ForeignKey(
        Siparis,
        on_delete=models.CASCADE,
        related_name='malzeme_gelisleri',
        blank=True,
        null=True,
        verbose_name="Satış Siparişi",
        help_text="Bu geliş hangi satış siparişi için"
    )
    satinalma_siparisi = models.ForeignKey(
        SatinAlmaSiparisi, 
        on_delete=models.CASCADE, 
        related_name='gelisler',
        verbose_name="Satın Alma Siparişi"
    )
    satinalma_kalemi = models.ForeignKey(
        SatinAlmaKalemi,
        on_delete=models.CASCADE,
        related_name='gelisler', 
        verbose_name="Satın Alma Kalemi"
    )
    
    # Geliş bilgileri
    gelen_miktar = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Gelen Miktar"
    )
    gelis_tarihi = models.DateField(
        default=timezone.now,
        verbose_name="Geliş Tarihi"
    )
    
    # Fiyat bilgileri
    KUR_CHOICES = [
        ('TRY', 'Türk Lirası (₺)'),
        ('USD', 'Amerikan Doları ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'İngiliz Sterlini (£)'),
    ]
    
    birim_fiyat = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=0,
        verbose_name="Birim Fiyat"
    )
    para_birimi = models.CharField(
        max_length=3,
        choices=KUR_CHOICES,
        default='TRY',
        verbose_name="Para Birimi"
    )
    toplam_tutar = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Toplam Tutar"
    )
    
    # Evrak bilgileri
    irsaliye_no = models.CharField(
        max_length=100,
        verbose_name="İrsaliye No"
    )
    fatura_no = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Fatura No"
    )
    
    # Dosya
    evrak_dosyasi = models.FileField(
        upload_to='malzeme_gelis_dosyalari/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Evrak Dosyası",
        help_text="İrsaliye, fatura vb. dökümanları yükleyebilirsiniz"
    )
    
    # Sistem bilgileri
    kayit_tarihi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Kayıt Tarihi"
    )
    kaydeden = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kaydeden"
    )
    
    # Notlar
    notlar = models.TextField(
        blank=True,
        verbose_name="Notlar"
    )
    
    class Meta:
        verbose_name = "Malzeme Geliş"
        verbose_name_plural = "Malzeme Gelişler"
        ordering = ['-gelis_tarihi', '-kayit_tarihi']
    
    def __str__(self):
        try:
            if self.satinalma_siparisi and self.satinalma_kalemi and self.satinalma_kalemi.malzeme_ihtiyaci:
                return f"{self.satinalma_siparisi.siparis_no} - {self.satinalma_kalemi.malzeme_ihtiyaci.malzeme_adi} ({self.gelen_miktar})"
        except Exception:
            pass
        return f"Malzeme Geliş #{self.pk}" if self.pk else "Yeni Malzeme Geliş"
    
    def clean(self):
        """Validasyon kontrolları"""
        from django.core.exceptions import ValidationError
        
        if self.gelen_miktar and self.gelen_miktar <= 0:
            raise ValidationError('Gelen miktar 0\'dan büyük olmalıdır!')
        
        # Toplam gelen miktar, sipariş edilen miktarı geçemez
        # satinalma_kalemi_id kullanarak güvenli erişim
        if hasattr(self, 'satinalma_kalemi_id') and self.satinalma_kalemi_id:
            try:
                # ForeignKey'e güvenli erişim
                satinalma_kalemi = self.satinalma_kalemi
                if satinalma_kalemi:
                    toplam_gelen = MalzemeGelis.objects.filter(
                        satinalma_kalemi_id=self.satinalma_kalemi_id
                    ).exclude(id=self.id).aggregate(
                        toplam=models.Sum('gelen_miktar')
                    )['toplam'] or 0
                    
                    if (toplam_gelen + (self.gelen_miktar or 0)) > satinalma_kalemi.miktar:
                        raise ValidationError(
                            f'Toplam gelen miktar ({toplam_gelen + self.gelen_miktar}) '
                            f'sipariş edilen miktarı ({satinalma_kalemi.miktar}) geçemez!'
                        )
            except Exception:
                # Eğer foreign key erişiminde sorun varsa, validasyonu atla
                pass
    
    def save(self, *args, **kwargs):
        """Kayıt sırasında toplam tutarı otomatik hesapla ve sipariş durumunu güncelle"""
        if self.birim_fiyat and self.gelen_miktar:
            self.toplam_tutar = self.birim_fiyat * self.gelen_miktar
        
        super().save(*args, **kwargs)
        
        # Malzeme gelişi kaydedildikten sonra sipariş durumunu kontrol et
        self._check_and_update_order_status()
    
    def _check_and_update_order_status(self):
        """Sipariş durumunu kontrol et ve gerekiyorsa güncelle"""
        try:
            siparis = self.satinalma_siparisi
            
            # Siparişin tüm kalemlerini kontrol et
            tum_kalemler_tamamlandi = True
            
            for kalem in siparis.kalemler.all():
                if kalem.gelis_durumu != 'tam' and kalem.gelis_durumu != 'fazla':
                    tum_kalemler_tamamlandi = False
                    break
            
            # Eğer tüm kalemler tamamlandıysa siparişi kapat
            if tum_kalemler_tamamlandi and siparis.durum != 'tamamlandi':
                # Sipariş durumunu güncelle
                siparis.durum = 'tamamlandi'
                siparis.save(update_fields=['durum'])
                
                # Sipariş kapatma notunu sisteme ekle
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # Sistem kullanıcısı varsa kaydet, yoksa None olsun
                try:
                    sistem_user = User.objects.filter(username='sistem').first()
                except:
                    sistem_user = None
                
                # SatinAlmaTeslimGuncelleme sınıfını kullan (aynı dosyada tanımlı)
                SatinAlmaTeslimGuncelleme.objects.create(
                    siparis=siparis,
                    eski_teslim_tarihi=siparis.guncel_teslim_tarihi or siparis.teslim_tarihi,
                    yeni_teslim_tarihi=siparis.guncel_teslim_tarihi or siparis.teslim_tarihi,
                    guncelleyen=sistem_user,
                    aciklama="Tüm kalemler tamamlandı - Sipariş otomatik kapatıldı"
                )
                
        except Exception as e:
            # Hata durumunda sessizce devam et (log tutabilir)
            pass
    
    @property 
    def malzeme_birim(self):
        """İlgili malzemenin birimini getir"""
        try:
            if self.satinalma_kalemi and self.satinalma_kalemi.malzeme_ihtiyaci:
                return self.satinalma_kalemi.malzeme_ihtiyaci.birim
        except Exception:
            pass
        return ""

# =============================================================================
# ÜRETİM MODÜLÜ
# =============================================================================

class StandardIsAdimi(models.Model):
    """Standart iş adımları kütüphanesi"""
    
    KATEGORI_CHOICES = [
        ('kesim', 'Kesim İşlemleri'),
        ('isleme', 'İşleme'),
        ('montaj', 'Montaj'),
        ('kalite', 'Kalite Kontrol'),
        ('paketleme', 'Paketleme'),
        ('boya', 'Boyama/Kaplama'),
        ('kaynak', 'Kaynak'),
        ('tornalama', 'Tornalama'),
        ('frezeleme', 'Frezeleme'),
        ('zimpara', 'Zımpara'),
    ]
    
    kod = models.CharField(max_length=20, unique=True, verbose_name="İş Adımı Kodu")
    ad = models.CharField(max_length=100, verbose_name="İş Adımı")
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, verbose_name="Kategori")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    tahmini_sure_birim = models.DecimalField(
        max_digits=8, decimal_places=2, 
        verbose_name="Tahmini Süre (dk/adet)",
        help_text="1 adet için ortalama süre"
    )
    gerekli_istasyon_tipi = models.CharField(
        max_length=20, 
        choices=[
            ('makine', 'Makine'),
            ('el_iscilik', 'El İşçiliği'),
            ('montaj', 'Montaj'),
            ('kalite_kontrol', 'Kalite Kontrol'),
            ('paketleme', 'Paketleme'),
        ],
        verbose_name="Gerekli İstasyon Tipi"
    )
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Renk kodlama (görsel tasarım için)
    renk = models.CharField(
        max_length=7, default="#007bff", 
        verbose_name="Renk Kodu",
        help_text="Hex renk kodu (örn: #007bff)"
    )
    ikon = models.CharField(
        max_length=50, blank=True,
        verbose_name="Font Awesome İkon",
        help_text="Örn: fas fa-cut, fas fa-hammer"
    )
    
    class Meta:
        verbose_name = "Standard İş Adımı"
        verbose_name_plural = "Standard İş Adımları" 
        ordering = ['kategori', 'ad']
    
    def __str__(self):
        return f"{self.kod} - {self.ad}"

class IsIstasyonu(models.Model):
    """Üretim iş istasyonları (makineler, el işçiliği vb.)"""
    
    ISTASYON_TIPLERI = [
        ('makine', 'Makine'),
        ('el_iscilik', 'El İşçiliği'),
        ('montaj', 'Montaj'),
        ('kalite_kontrol', 'Kalite Kontrol'),
        ('paketleme', 'Paketleme'),
        ('depo', 'Depo/Sevkiyat'),
    ]
    
    DURUM_CHOICES = [
        ('aktif', 'Aktif'),
        ('bakim', 'Bakımda'),
        ('arizali', 'Arızalı'),
        ('pasif', 'Pasif'),
    ]
    
    # Temel Bilgiler
    kod = models.CharField(max_length=20, unique=True, verbose_name="İstasyon Kodu")
    ad = models.CharField(max_length=100, verbose_name="İstasyon Adı")
    tip = models.CharField(max_length=20, choices=ISTASYON_TIPLERI, verbose_name="İstasyon Tipi")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='aktif', verbose_name="Durum")
    
    # Konum ve Fiziksel Bilgiler
    lokasyon = models.CharField(max_length=100, blank=True, verbose_name="Lokasyon/Adres")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    
    # Kapasite Bilgileri
    gunluk_calisma_saati = models.DecimalField(
        max_digits=4, decimal_places=2,
        default=8.0,
        verbose_name="Günlük Çalışma Saati"
    )
    
    # Maliyet Bilgileri
    saatlik_maliyet = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name="Saatlik Maliyet (TL)",
        help_text="İşçilik + makine maliyeti/saat"
    )
    
    # Operatör Bilgileri
    gerekli_operator_sayisi = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Gerekli Operatör Sayısı"
    )
    
    # Sistem Bilgileri
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    olusturan = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        verbose_name="Oluşturan"
    )
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "İş İstasyonu"
        verbose_name_plural = "İş İstasyonları"
        ordering = ['kod']
    
    def __str__(self):
        return f"{self.kod} - {self.ad}"
    
    @property
    def gunluk_kapasite(self):
        """Günlük toplam kapasite"""
        return float(self.saatlik_kapasite) * float(self.gunluk_calisma_saati)
    
    @property
    def durum_renk(self):
        """Durum için renk kodu"""
        renkler = {
            'aktif': '#28a745',
            'bakim': '#ffc107', 
            'arizali': '#dc3545',
            'pasif': '#6c757d'
        }
        return renkler.get(self.durum, '#6c757d')
    
    @property
    def doluluk_orani(self):
        """Mevcut doluluk oranı (şimdilik sabit, ileride gerçek verilerle hesaplanacak)"""
        # TODO: Gerçek iş emirleri üzerinden hesapla
        return 0


class IsAkisi(models.Model):
    """Ürün üretim süreç akışları"""
    
    AKIS_TIPLERI = [
        ('seri', 'Seri İşlem'),
        ('paralel', 'Paralel İşlem'),
    ]
    
    # Temel Bilgiler
    kod = models.CharField(max_length=20, unique=True, verbose_name="Akış Kodu")
    ad = models.CharField(max_length=100, verbose_name="Akış Adı")
    urun = models.ForeignKey(
        Urun, on_delete=models.CASCADE, 
        related_name='is_akislari',
        verbose_name="Ürün"
    )
    versiyon = models.CharField(max_length=10, default='1.0', verbose_name="Versiyon")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    
    # Akış Bilgileri
    tip = models.CharField(max_length=10, choices=AKIS_TIPLERI, default='seri', verbose_name="Akış Tipi")
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Sistem Bilgileri
    olusturan = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        verbose_name="Oluşturan"
    )
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "İş Akışı"
        verbose_name_plural = "İş Akışları"
        ordering = ['urun', 'kod']
        unique_together = ['urun', 'versiyon']
    
    def __str__(self):
        return f"{self.kod} - {self.ad} (v{self.versiyon})"
    
    @property
    def toplam_operasyon_sayisi(self):
        """Toplam operasyon sayısı"""
        return self.operasyonlar.count()
    
    @property
    def tahmini_sure(self):
        """Tahmini toplam işlem süresi (dakika)"""
        if self.tip == 'seri':
            return sum([op.standart_sure for op in self.operasyonlar.all()])
        else:  # paralel
            return max([op.standart_sure for op in self.operasyonlar.all()] or [0])
    
    @property 
    def kritik_yol(self):
        """Kritik yol operasyonları (en uzun süren yol)"""
        # TODO: Gerçek kritik yol algoritması implementasyonu
        return self.operasyonlar.filter(kritik=True)


class IsAkisiOperasyon(models.Model):
    """İş akışı içindeki tek operasyon"""
    
    # İlişkiler
    is_akisi = models.ForeignKey(
        IsAkisi, on_delete=models.CASCADE,
        related_name='operasyonlar',
        verbose_name="İş Akışı"
    )
    istasyon = models.ForeignKey(
        IsIstasyonu, on_delete=models.PROTECT,
        verbose_name="İş İstasyonu"
    )
    standart_adim = models.ForeignKey(
        StandardIsAdimi, on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Standart İş Adımı"
    )
    
    # Operasyon Bilgileri
    sira_no = models.PositiveSmallIntegerField(verbose_name="Sıra No", editable=False)
    operasyon_adi = models.CharField(max_length=100, verbose_name="Operasyon Adı")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    
    # Süre ve Kapasite
    standart_sure = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name="Standart Süre (dakika)",
        help_text="1 adet için standart işlem süresi"
    )
    hazirlik_suresi = models.DecimalField(
        max_digits=8, decimal_places=2, 
        default=0,
        verbose_name="Hazırlık Süresi (dakika)",
        help_text="İş başlangıcında tek seferlik hazırlık süresi"
    )
    
    # Kalite ve Kontrol
    kalite_kontrolu_gerekli = models.BooleanField(
        default=False,
        verbose_name="Kalite Kontrolü Gerekli"
    )
    kritik = models.BooleanField(
        default=False,
        verbose_name="Kritik Operasyon",
        help_text="Kritik yol üzerinde mi?"
    )
    
    # Malzeme Gereklilikleri
    operasyon_malzemeleri = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Operasyon Malzemeleri",
        help_text="Bu operasyonda kullanılacak spesifik malzemeler (BOM'dan seçilen)"
    )
    operasyon_ara_urunleri = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Operasyon Ara Ürünleri", 
        help_text="Bu operasyonda kullanılacak spesifik ara ürünler (BOM'dan seçilen)"
    )
    
    # Bağımlılıklar
    onceki_operasyonlar = models.ManyToManyField(
        'self', 
        symmetrical=False,
        blank=True,
        verbose_name="Önceki Operasyonlar",
        help_text="Bu operasyondan önce tamamlanması gereken operasyonlar"
    )
    
    class Meta:
        verbose_name = "İş Akışı Operasyonu"
        verbose_name_plural = "İş Akışı Operasyonları"
        ordering = ['is_akisi', 'sira_no']
        unique_together = ['is_akisi', 'sira_no']
    
    def __str__(self):
        return f"{self.sira_no:02d}. {self.operasyon_adi} ({self.istasyon})"
    
    def save(self, *args, **kwargs):
        """Kaydet sırasında sıra no otomatik ata"""
        if self.sira_no is None or self.sira_no == 0:
            # Bu iş akışındaki en büyük sıra no'yu bul
            max_sira = IsAkisiOperasyon.objects.filter(
                is_akisi=self.is_akisi
            ).aggregate(
                max_sira=models.Max('sira_no')
            )['max_sira']
            
            self.sira_no = (max_sira or 0) + 1
        
        super().save(*args, **kwargs)
    
    @property
    def toplam_sure(self):
        """Toplam süre (hazırlık + standart)"""
        return float(self.hazirlik_suresi) + float(self.standart_sure)
    
    @property
    def onceki_operasyon_sayisi(self):
        """Önceki operasyon sayısı"""
        return self.onceki_operasyonlar.count()
    
    def is_ready_to_start(self, tamamlanan_operasyonlar=None):
        """Operasyon başlamaya hazır mı?"""
        if tamamlanan_operasyonlar is None:
            tamamlanan_operasyonlar = []
        
        # Tüm önceki operasyonlar tamamlandı mı?
        for onceki in self.onceki_operasyonlar.all():
            if onceki.id not in tamamlanan_operasyonlar:
                return False
        return True


class IsEmri(models.Model):
    """Üretim iş emirleri - Her operasyon için ayrı iş emri"""
    
    DURUM_CHOICES = [
        ('planlandi', 'Planlandı'),
        ('malzeme_bekliyor', 'Malzeme Bekliyor'),
        ('ara_urun_bekliyor', 'Ara Ürün Bekliyor'),
        ('hazir', 'Hazır'),
        ('basladi', 'Başladı'),
        ('devam_ediyor', 'Devam Ediyor'),
        ('beklemede', 'Beklemede'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal'),
    ]
    
    ONCELIK_CHOICES = [
        ('dusuk', 'Düşük'),
        ('normal', 'Normal'),
        ('yuksek', 'Yüksek'),
        ('acil', 'Acil'),
    ]
    
    # Temel Bilgiler
    emirNo = models.CharField(max_length=50, unique=True, verbose_name="İş Emri No")
    siparis = models.ForeignKey(
        Siparis, on_delete=models.CASCADE,
        related_name='is_emirleri',
        verbose_name="Sipariş"
    )
    siparis_kalemi = models.ForeignKey(
        SiparisKalem, on_delete=models.CASCADE,
        related_name='is_emirleri',
        blank=True, null=True,
        verbose_name="Sipariş Kalemi"
    )
    urun = models.ForeignKey(
        Urun, on_delete=models.PROTECT,
        verbose_name="Ürün"
    )
    is_akisi = models.ForeignKey(
        IsAkisi, on_delete=models.PROTECT,
        verbose_name="İş Akışı"
    )
    
    # Operasyon Bilgisi - Her iş emri tek operasyon için
    operasyon = models.ForeignKey(
        IsAkisiOperasyon, on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Operasyon"
    )
    
    # Ana İş Emri Grubu - Aynı siparişten çıkan tüm operasyon emirleri
    ana_emirNo = models.CharField(max_length=30, default="TEMP", verbose_name="Ana İş Emri No", help_text="Bu siparişin tüm operasyonları için ortak numara")
    
    # Gereklilikler (JSON format)
    gerekli_malzemeler = models.JSONField(default=list, verbose_name="Gerekli Malzemeler", help_text="Bu operasyon için gerekli malzemeler")
    gerekli_ara_urunler = models.JSONField(default=list, verbose_name="Gerekli Ara Ürünler", help_text="Bu operasyon için gerekli ara ürünler")
    onceki_operasyonlar = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False,
        related_name='sonraki_operasyonlar',
        verbose_name="Önceki Operasyonlar",
        help_text="Bu operasyondan önce tamamlanması gereken operasyonlar"
    )
    
    # Miktar ve Hedef
    planlanan_miktar = models.PositiveIntegerField(default=1, verbose_name="Planlanan Miktar")
    uretilen_miktar = models.PositiveIntegerField(default=0, verbose_name="Üretilen Miktar")
    
    # Planlama Bilgileri
    planlanan_istasyon = models.ForeignKey(IsIstasyonu, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Planlanan İstasyon")
    planlanan_baslangic_tarihi = models.DateField(default="2024-01-01", verbose_name="Planlanan Başlangıç Tarihi")
    planlanan_baslangic_saati = models.TimeField(default="08:00", verbose_name="Planlanan Başlangıç Saati")
    planlanan_bitis_tarihi = models.DateField(default="2024-01-01", verbose_name="Planlanan Bitiş Tarihi") 
    planlanan_bitis_saati = models.TimeField(default="17:00", verbose_name="Planlanan Bitiş Saati")
    planlanan_sure = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Planlanan Süre (dakika)")
    
    # Gerçekleşen Tarihleri
    gercek_baslangic_tarihi = models.DateField(null=True, blank=True, verbose_name="Gerçek Başlangıç Tarihi")
    gercek_baslangic_saati = models.TimeField(null=True, blank=True, verbose_name="Gerçek Başlangıç Saati")
    gercek_bitis_tarihi = models.DateField(null=True, blank=True, verbose_name="Gerçek Bitiş Tarihi")
    gercek_bitis_saati = models.TimeField(null=True, blank=True, verbose_name="Gerçek Bitiş Saati")
    gercek_sure = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Gerçek Süre (dakika)")
    
    # Durum ve Öncelik
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='planlandi', verbose_name="Durum")
    oncelik = models.CharField(max_length=10, choices=ONCELIK_CHOICES, default='normal', verbose_name="Öncelik")
    
    # Notlar ve Açıklamalar
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    notlar = models.TextField(blank=True, verbose_name="Üretim Notları")
    
    # Sistem Bilgileri
    olusturan = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='olusturulan_is_emirleri',
        verbose_name="Oluşturan"
    )
    sorumlu = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sorumlu_is_emirleri',
        verbose_name="Sorumlu"
    )
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "İş Emri"
        verbose_name_plural = "İş Emirleri"
        ordering = ['-olusturulma_tarihi']
    
    def __str__(self):
        return f"{self.emirNo} - {self.operasyon.operasyon_adi} ({self.planlanan_miktar} adet)"
    
    def save(self, *args, **kwargs):
        """Kayıt sırasında iş emri no oluştur"""
        if not self.emirNo:
            from datetime import datetime
            self.emirNo = f"IE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        super().save(*args, **kwargs)
    
    @property
    def tamamlanma_orani(self):
        """Tamamlanma oranı yüzdesi"""
        if self.planlanan_miktar <= 0:
            return 0
        return min(100, (self.uretilen_miktar / self.planlanan_miktar) * 100)
    
    @property
    def durum_renk(self):
        """Durum için renk kodu"""
        renkler = {
            'planlandi': '#6c757d',
            'malzeme_bekliyor': '#fd7e14',
            'ara_urun_bekliyor': '#e83e8c',
            'hazir': '#20c997',
            'basladi': '#17a2b8',
            'devam_ediyor': '#007bff',
            'beklemede': '#ffc107',
            'tamamlandi': '#28a745',
            'iptal': '#dc3545'
        }
        return renkler.get(self.durum, '#6c757d')
    
    @property
    def planlanan_baslangic(self):
        """Backward compatibility için datetime property"""
        if self.planlanan_baslangic_tarihi and self.planlanan_baslangic_saati:
            from datetime import datetime
            from django.utils import timezone
            naive_datetime = datetime.combine(self.planlanan_baslangic_tarihi, self.planlanan_baslangic_saati)
            return timezone.make_aware(naive_datetime)
        return None
        
    @property
    def planlanan_bitis(self):
        """Backward compatibility için datetime property"""
        if self.planlanan_bitis_tarihi and self.planlanan_bitis_saati:
            from datetime import datetime
            from django.utils import timezone
            naive_datetime = datetime.combine(self.planlanan_bitis_tarihi, self.planlanan_bitis_saati)
            return timezone.make_aware(naive_datetime)
        return None
        
    @property
    def gercek_baslangic(self):
        """Backward compatibility için datetime property"""
        if self.gercek_baslangic_tarihi and self.gercek_baslangic_saati:
            from datetime import datetime
            from django.utils import timezone
            naive_datetime = datetime.combine(self.gercek_baslangic_tarihi, self.gercek_baslangic_saati)
            return timezone.make_aware(naive_datetime)
        return None
    
    def hesapla_uretim_hazir_tarihi(self):
        """Üretime hazır olma tarihini hesaplar"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        import json
        
        hazir_tarihleri = []
        
        # 1. Malzeme hazır olma tarihi
        malzeme_hazir_tarihi = self.hesapla_malzeme_hazir_tarihi()
        if malzeme_hazir_tarihi:
            hazir_tarihleri.append(malzeme_hazir_tarihi)
        
        # 2. Bağımlı operasyonların tamamlanma tarihi
        bagimlillik_tarihi = self.hesapla_bagimlillik_hazir_tarihi()
        if bagimlillik_tarihi:
            hazir_tarihleri.append(bagimlillik_tarihi)
        
        # 3. Ara ürün hazır olma tarihi
        ara_urun_tarihi = self.hesapla_ara_urun_hazir_tarihi()
        if ara_urun_tarihi:
            hazir_tarihleri.append(ara_urun_tarihi)
        
        # En geç tarih seçilir
        if hazir_tarihleri:
            return max(hazir_tarihleri)
        
        # Hiçbir engel yoksa bugün hazır
        return timezone.now().date()
    
    def hesapla_malzeme_hazir_tarihi(self):
        """Bu operasyon için gerekli malzemelerin hazır olacağı tarihi hesaplar"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        from django.db.models import Q
        
        # print(f"MATERIAL DATE CALLED for IsEmri ID: {self.id}")
        
        # Operasyon yoksa bugün hazır
        if not self.operasyon:
            # print(f"No operation for IsEmri {self.id}, returning today")
            return timezone.now().date()
        
        # Bu sipariş için malzeme ihtiyaçlarını bul
        if not (self.siparis_kalemi and self.siparis_kalemi.siparis):
            # Sipariş kalemi yoksa operasyon tipine göre karar ver
            if self.operasyon:
                op_adi = str(self.operasyon.operasyon_adi).lower()
                if 'sargı' in op_adi:
                    # Sargı operasyonları için genel malzeme tarihi (25.08.2025)
                    from datetime import date
                    return date(2025, 8, 25)
                elif any(x in op_adi for x in ['montaj', 'kurutma', 'test']):
                    # Montaj/kurutma/test için stoktan - bugün hazır
                    return timezone.now().date()
            return timezone.now().date()
            
        # Montaj/kurutma/test operasyonları için malzeme kontrolü yapma
        if self.operasyon:
            op_adi = str(self.operasyon.operasyon_adi).lower()
            if any(x in op_adi for x in ['montaj', 'kurutma', 'test']):
                # print(f"OVERRIDE - {op_adi} operasyonu için stoktan malzeme")
                return timezone.now().date()
            
        # Bu siparişle ilgili malzeme ihtiyaçlarını bul
        
        # SQLite JSON contains desteklemediği için tüm malzeme ihtiyaçlarını getir ve filtrele
        import json
        
        malzeme_ihtiyaclar = MalzemeIhtiyac.objects.all()
        siparis_no = self.siparis_kalemi.siparis.siparis_no
        
        en_gec_tarih = timezone.now().date()
        bulunan_ihtiyac = 0
        bulunan_kalem = 0
        
        # Debug: Toplam kayıt sayıları
        # print(f"DEBUG - Total MalzemeIhtiyac: {malzeme_ihtiyaclar.count()}")
        # print(f"DEBUG - Siparis NO: {siparis_no}")
        
        for ihtiyac in malzeme_ihtiyaclar:
            # JSON field'ında sipariş numarası var mı kontrol et
            try:
                ilgili_siparisler = ihtiyac.ilgili_siparisler or []
                if siparis_no not in str(ilgili_siparisler):
                    continue
                bulunan_ihtiyac += 1
                # print(f"DEBUG - Found requirement ID: {ihtiyac.id}")
            except:
                continue
                
            # Stoktan kullanılacak malzemeler için tarih hesaplaması yapma
            if ihtiyac.islem_tipi == 'stoktan_kullan':
                # print(f"SKIP - Stoktan kullan ID {ihtiyac.id}")
                continue
            else:
                # print(f"PROCESS - Satin al ID {ihtiyac.id}")
                
                # Bu malzeme için satın alma siparişlerini bul
                satinalma_kalemleri = SatinAlmaKalemi.objects.filter(
                    malzeme_ihtiyaci=ihtiyac,
                    siparis__durum__in=['bekliyor', 'onaylandi', 'gonderildi']
                )
                
                # print(f"DEBUG - Item count for requirement ID {ihtiyac.id}: {satinalma_kalemleri.count()}")
                
                # En erken gelecek malzeme tarihini al
                for kalem in satinalma_kalemleri:
                    bulunan_kalem += 1
                    # SatinAlmaKalemi'nden sipariş tarihini al
                    siparis_teslim = kalem.siparis.guncel_teslim_tarihi or kalem.siparis.teslim_tarihi
                    # print(f"DEBUG - Kalem teslim tarihi: {siparis_teslim}")
                    if siparis_teslim and siparis_teslim > en_gec_tarih:
                        en_gec_tarih = siparis_teslim
        
        # print(f"DEBUG - Found requirements: {bulunan_ihtiyac}, Found items: {bulunan_kalem}")
        # print(f"DEBUG - Final tarih: {en_gec_tarih}")
        
        # Eğer hiç malzeme verisi bulunamadıysa sipariş durumuna göre default tarih ver
        if bulunan_ihtiyac == 0:
            # print("DEBUG - No material requirements found, using default date")
            if self.siparis_kalemi.siparis.durum == 'malzeme_planlandi':
                return timezone.now().date() + timedelta(days=7)
            else:
                return timezone.now().date() + timedelta(days=14)
                
        return en_gec_tarih
    
    def hesapla_bagimlillik_hazir_tarihi(self):
        """Bağımlı operasyonların tamamlanma tarihini hesaplar"""
        # Bu operasyondan önce tamamlanması gereken operasyonları bul
        if not self.operasyon or not self.siparis_kalemi:
            return None
            
        onceki_operasyonlar = IsEmri.objects.filter(
            siparis_kalemi=self.siparis_kalemi,
            operasyon__sira_no__lt=self.operasyon.sira_no,
            planlanan_istasyon__isnull=False  # Sadece planlanmış olanları dikkate al
        ).exclude(id=self.id)
        
        hazir_tarihleri = []
        
        for onceki_emir in onceki_operasyonlar:
            if onceki_emir.durum in ['tamamlandi']:
                continue  # Zaten tamamlanmış
            
            # Planlanan bitiş tarihi varsa onu kullan
            if onceki_emir.planlanan_bitis_tarihi:
                hazir_tarihleri.append(onceki_emir.planlanan_bitis_tarihi)
            else:
                # Yoksa bu operasyonun süresi + başlangıç tarihi
                if onceki_emir.planlanan_baslangic_tarihi and onceki_emir.planlanan_sure:
                    from datetime import timedelta
                    bitis = onceki_emir.planlanan_baslangic_tarihi + timedelta(
                        minutes=float(onceki_emir.planlanan_sure or 0)
                    )
                    hazir_tarihleri.append(bitis)
        
        return max(hazir_tarihleri) if hazir_tarihleri else None
    
    def hesapla_ara_urun_hazir_tarihi(self):
        """Ara ürün bağımlılığı varsa onun hazır olma tarihini hesaplar"""
        # Bu operasyonun ürettiği ürün başka bir operasyonun girdisi ise
        # o operasyonun tamamlanma tarihini bekle
        
        # BOM'da bu ürünü kullanan başka ürünler var mı?
        if self.urun.kategori != 'ara_urun':
            return None
        
        # Bu ara ürünü üreten önceki iş emirlerini bul
        ara_urun_emirleri = IsEmri.objects.filter(
            urun=self.urun,
            durum__in=['planlandi', 'malzeme_bekliyor', 'hazir', 'basladi']
        ).exclude(id=self.id)
        
        if not ara_urun_emirleri.exists():
            return None
        
        # En erken tamamlanacak ara ürün emrinin tarihini al
        hazir_tarihleri = []
        for emir in ara_urun_emirleri:
            if emir.planlanan_bitis_tarihi:
                hazir_tarihleri.append(emir.planlanan_bitis_tarihi)
        
        return min(hazir_tarihleri) if hazir_tarihleri else None
    
    @property
    def uretim_hazir_tarihi(self):
        """Template'lerde kullanılmak üzere property"""
        return self.hesapla_uretim_hazir_tarihi()
    
    @property 
    def hazirlik_durumu(self):
        """Hazırlık durumunu belirle"""
        from datetime import timedelta
        try:
            hazir_tarihi = self.hesapla_uretim_hazir_tarihi()
            bugun = timezone.now().date()
            
            if hazir_tarihi <= bugun:
                return 'hazir'
            elif hazir_tarihi <= bugun + timedelta(days=3):
                return 'yaklasyor'
            else:
                return 'bekliyor'
        except:
            return 'bilinmiyor'
        
    @property
    def gercek_bitis(self):
        """Backward compatibility için datetime property"""
        if self.gercek_bitis_tarihi and self.gercek_bitis_saati:
            from datetime import datetime
            from django.utils import timezone
            naive_datetime = datetime.combine(self.gercek_bitis_tarihi, self.gercek_bitis_saati)
            return timezone.make_aware(naive_datetime)
        return None
        
    def gereklilikler_hazir_mi(self):
        """Tüm gereklilikler hazır mı kontrol et"""
        # Malzeme gereklilikleri
        for malzeme in self.gerekli_malzemeler:
            # Stok kontrolü yapılabilir
            pass
            
        # Ara ürün gereklilikleri
        for ara_urun in self.gerekli_ara_urunler:
            # Ara ürün iş emirleri tamamlandı mı kontrol edilebilir
            pass
            
        # Önceki operasyonlar tamamlandı mı
        for onceki_operasyon in self.onceki_operasyonlar.all():
            if onceki_operasyon.durum != 'tamamlandi':
                return False
                
        return True
    
    @property
    def oncelik_renk(self):
        """Öncelik için renk kodu"""
        renkler = {
            'dusuk': '#28a745',
            'normal': '#17a2b8',
            'yuksek': '#ffc107',
            'acil': '#dc3545'
        }
        return renkler.get(self.oncelik, '#17a2b8')
    
    @property
    def gecikme_durumu(self):
        """Gecikme durumu"""
        from django.utils import timezone
        simdi = timezone.now()
        
        if self.durum == 'tamamlandi':
            if self.gercek_bitis and self.gercek_bitis > self.planlanan_bitis:
                return 'gecikti'
            return 'zamaninda'
        elif simdi > self.planlanan_bitis:
            return 'gecikmede'
        return 'zamaninda'
    


