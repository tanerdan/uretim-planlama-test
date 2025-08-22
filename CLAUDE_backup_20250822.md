# 📋 Üretim Planlama Yazılımı - Claude Code Dokümantasyonu

## 🎯 Proje Hakkında
Django tabanlı üretim planlama sistemi. Müşteri siparişlerinden başlayarak malzeme ihtiyaç planlaması ve satın alma süreçlerini yönetir.

## 🏗️ Proje Yapısı
```
D:\Documents_D\SoftwareDevelopment\uretim-planlama\
├── venv\                    # Virtual environment
├── backend\
│   ├── production\         # Ana uygulama
│   │   ├── models.py      # 13 model tanımlı
│   │   ├── admin.py       # Admin özelleştirmeleri
│   │   ├── serializers.py # API serializers
│   │   ├── views.py       # API views
│   │   ├── urls.py        # API routes
│   │   └── templates/admin/  # Custom templates
│   ├── settings.py        # Django ayarları
│   └── urls.py           # Ana URL yapılandırması
├── media\                 # Yüklenen dosyalar
├── manage.py
└── requirements.txt
```

## 🚀 Kurulum ve Çalıştırma
```bash
# Virtual environment aktifleştir
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanı migrasyonları
python manage.py migrate

# Süper kullanıcı oluştur (gerekirse)
python manage.py createsuperuser

# Sunucuyu başlat
python manage.py runserver

# Admin paneline erişim
http://127.0.0.1:8000/admin/
```

## ✅ Tamamlanan Özellikler

### 1. Temel Modüller
- **Müşteri Yönetimi**: Tam CRUD, iletişim bilgileri, aktif/pasif durumu
- **Ürün Yönetimi**: Hammadde/ara ürün/bitmiş ürün kategorileri, stok takibi
- **Sipariş Yönetimi**: Müşteri siparişleri, çoklu kalem, dosya yükleme
- **BOM (Bill of Materials)**: Çok seviyeli ürün reçeteleri

### 2. MRP (Malzeme İhtiyaç Planlama) ⭐
- Bekleyen siparişleri toplu seçme
- BOM'ları **derinlemesine analiz** (ara ürünleri açarak hammaddelere ulaşma)
- **Recursif malzeme hesaplama** - çok seviyeli BOM desteği
- Malzeme ihtiyacı için "Satın Al" / "Stoktan Kullan" seçimi
- Malzeme ihtiyaçlarını veritabanına kaydetme
- İlgili sipariş ve ürün bilgilerini JSON olarak saklama

### 3. Satın Alma Modülü ⭐
- **Tedarikçi yönetimi**: Tam bilgi seti, vergi bilgileri
- **Satın alma siparişi oluşturma**: Malzeme ihtiyaçlarından otomatik
- **Çoklu para birimi**: Her satır için ayrı para birimi
- **Esnek teslimat**: Her malzeme için ayrı teslim tarihi
- **Sipariş export/yazdırma**: PDF template hazır
- **Güncel teslim tarihi takibi**: Orijinal vs güncel tarih
- **Değişiklik geçmişi**: Tüm teslim tarihi güncellemeleri kayıt altında
- **Liste görünümünden hızlı düzenleme**: Inline editing

### 4. Malzeme Geliş Sistemi ⭐
- **MalzemeGelis Modeli**: Satın alma siparişi ve kalemine bağlı
- **Çoklu para birimi**: TRY, USD, EUR, GBP desteği
- **Kısmi teslimat takibi**: Bekliyor/kısmi/tam/fazla durumları
- **Otomatik sipariş kapatma**: Tüm kalemler tamamlandığında
- **Raporlama sistemi**: Dashboard, performans analizi, Excel export

### 5. Üretim Modülü ⭐⭐ (21 Ağustos 2025)
- **İş İstasyonları**: Makine ve istasyon tanımları
- **Standart İş Adımları**: Operasyon template'leri
- **İş Akışları**: Ürün bazlı üretim süreç tanımları
- **Görsel İş Akışı Tasarımı**: Drag&drop ile workflow oluşturma
- **İş Emirleri**: Sipariş bazlı üretim emirleri
- **Recursif İş Emri Oluşturma**: Ana ürün + ara ürün emirleri otomatik
- **Operasyon-Malzeme Eşleştirmesi**: Her operasyona özel malzeme ataması
- **Bağımlılık Yönetimi**: Operasyonlar arası otomatik bağımlılık kurma

### 6. Üretim Planlama Gantt Sistemi ⭐⭐ (22 Ağustos 2025) - YENİ
- **Drag&Drop Planlama**: İş emirlerini istasyon ve tarihlere sürükle-bırak
- **Görsel Kapasite Takibi**: Her gün ve istasyon için kapasite göstergeleri
- **İstasyon+Gün Bazlı Mesai**: Her hücre için özel çalışma saati ayarlama
- **Kapasite Aşımı Yönetimi**: Sonraki güne otomatik taşıma seçeneği
- **Türkçe Decimal Format**: 6,0h gibi Türkçe ondalık sayı desteği
- **Unplan İşlemi**: Planlanmış işleri geri planlanmamış listeye taşıma
- **Malzeme Hazır Tarihi Kontrolü**: Malzeme gelişine göre planlama kısıtı
- **Gerçek Zamanlı Kapasite Hesaplama**: Çalışma saati değişikliklerinde anlık güncelleme

### 7. Durum Takibi ve Otomasyonlar
- **Sipariş Durumları**: `beklemede` → `malzeme_planlandi` → `is_emirleri_olusturuldu` → `uretimde` → `tamamlandi`
- **Malzeme İhtiyaç Durumları**: `beklemede` → `siparis_verildi` → `kismi_geldi` → `tamamlandi`
- **İş Emri Durumları**: `planlandi` → `malzeme_bekliyor` → `hazir` → `basladi` → `tamamlandi`
- **Otomatik Durum Güncellemeleri**: İş emri oluşturulduğunda sipariş durumu otomatik güncellenir

### 8. Görsel Malzeme Takibi ⭐ (21 Ağustos 2025)
- **Malzeme Kullanım İşaretleme**: Drop edilen malzemeler sol panelde görsel olarak işaretlenir
- **Kullanıldı Badge'leri**: Yeşil ✓ işareti ile kullanılan malzemeler
- **Şeffaflık ve Filtreler**: Kullanılan malzemeler %50 şeffaf + gri filtre
- **Hover Efektleri**: Animasyonlu geçişler ve büyütme efektleri
- **Otomatik Temizleme**: Canvas temizlendiğinde malzeme durumları sıfırlanır

### 9. Admin Panel Özelleştirmeleri
- **Görsel İş Akışı Editörü**: Custom template ile drag&drop arayüz
- **Üretim Planlama Gantt**: Tam özellikli drag&drop planlama arayüzü
- **AJAX Workflow Kaydetme**: Gerçek zamanlı workflow kaydetme
- **Smart Form Filtering**: İş emri formlarında akıllı filtreleme
- **Hover BOM görüntüleme**: Ürün listesinde reçete detayları
- **Stok durumu göstergeleri**: Renk kodlu durumlar
- **Toplu işlemler**: Çoklu sipariş seçimi ve planlama

## 📊 Veritabanı Modelleri

### Ana Modeller
1. **Musteri** - Müşteri bilgileri ve iletişim
2. **Urun** - Ürün tanımları (hammadde/ara ürün/bitmiş ürün)
3. **UrunRecete** - Ürün reçeteleri (BOM) - recursive yapı
4. **Siparis** - Müşteri siparişleri
5. **SiparisKalem** - Sipariş detay kalemleri
6. **SiparisDosya** - Sipariş ek dosyaları

### MRP Modülü
7. **MalzemePlanlama** (Proxy) - Planlama arayüzü
8. **MalzemeIhtiyac** - Hesaplanan malzeme ihtiyaçları

### Satın Alma Modülü
9. **Tedarikci** - Tedarikçi bilgileri
10. **SatinAlmaSiparisi** - Satın alma siparişleri (durum takibi eklendi)
11. **SatinAlmaKalemi** - Satın alma detay kalemleri (tamamlanma izleme)
12. **SatinAlmaTeslimGuncelleme** - Teslim tarihi değişiklik geçmişi

### Malzeme Geliş Modülü (13)
13. **MalzemeGelis** - Malzeme teslim alımları

### Üretim Modülü (14-19) ⭐ 
14. **IsIstasyonu** - İş istasyonları ve makineler
15. **StandardIsAdimi** - Standart operasyon template'leri
16. **IsAkisi** - Ürün bazlı iş akışları
17. **IsAkisiOperasyon** - İş akışı operasyonları (malzeme atamaları dahil)
18. **IsEmri** - Üretim iş emirleri
19. **IsEmriOperasyonDurum** - İş emri operasyon durum takibi

### Üretim Planlama Modülü (20-21) ⭐⭐ YENİ
20. **UretimPlanlama** (Proxy) - Üretim planlama arayüzü
21. **IsEmriPlanlama** - İş emri planlama detayları

## 🎨 Görsel İş Akışı Tasarımı ⭐⭐

### Özellikler
- **Drag & Drop Arayüzü**: Sol panelden canvas'a sürükle-bırak
- **İş Adımları**: Standart operasyonları canvas'a ekleme
- **BOM Malzemeleri**: Ürün reçetesinden otomatik malzeme listesi
- **Operasyon-Malzeme Eşleştirmesi**: Malzemeleri operasyonlara atama
- **Bağlantı Çizimi**: Operasyonlar arası bağımlılık tanımlama
- **Görsel Feedback**: Malzeme atamaları için animasyonlu geri bildirim
- **Otomatik Kaydetme**: Workflow ve malzeme atamaları veritabanına kayıt

### Kullanım Akışı
1. **Ürün Seçimi** → BOM malzemeleri yüklenir
2. **İş Adımları Ekleme** → Standard operasyonları canvas'a sürükle
3. **Malzeme Atama** → BOM malzemelerini operasyonlara sürükle
4. **Bağlantı Çizimi** → Operasyonlar arası bağımlılık tanımla
5. **Kaydetme** → Workflow ve malzeme atamaları kaydedilir
6. **İş Emri Oluşturma** → Siparişlerden bu workflow kullanılarak iş emri oluştur

## 🗓️ Üretim Planlama Gantt Sistemi ⭐⭐ (22 Ağustos 2025)

### Ana Özellikler
- **Gantt Chart Görünümü**: İstasyonlar x günler matrisi
- **Drag&Drop Planlama**: İş emirlerini sol panelden sürükle-bırak
- **Dinamik Kapasite Hesaplama**: Her hücre için gerçek zamanlı kapasite takibi
- **Çalışma Saati Yönetimi**: İstasyon+gün bazında özel mesai ayarlama
- **Malzeme Hazır Tarihi Kontrolü**: Malzeme gelişine göre planlama kısıtı

### Teknik Özellikler
- **Türkçe Decimal Format**: "6,0h" formatında süre desteği
- **Kapasite Aşımı Yönetimi**: Sonraki güne otomatik taşıma seçeneği
- **Unplan İşlevi**: Planlanmış işleri geri alma
- **Gerçek Zamanlı Validasyon**: Sürüklerken anlık geri bildirim
- **AJAX Kaydetme**: Veritabanına otomatik kayıt

### Validasyon Kuralları
1. **Çalışma Saati Kontrolü**: 0 saatlik günlere planlama yapılamaz
2. **Kapasite Kontrolü**: Günlük kapasiteyi aşan işler için uyarı
3. **Malzeme Hazır Tarihi**: Malzemeler gelişinden önce planlama yapılamaz
4. **Overflow Handling**: Taşan süreler için sonraki güne taşıma seçeneği

## 💡 Önemli Teknik Notlar

### Yeni Üretim Algoritmaları
- **Recursif İş Emri Oluşturma**: Ana ürün için iş emri oluştururken, BOM'daki ara ürünler için de otomatik iş emri oluşturma
- **Akıllı Bağımlılık Kurma**: İş akışındaki operasyon sırası + ara ürün bağımlılıkları otomatik kurulur
- **Operasyon-Malzeme Mapping**: Her operasyona özel malzeme gereklilikleri JSON field'da saklanır
- **Görsel Malzeme Takibi**: JavaScript ile malzeme kullanım durumu görsel olarak takip edilir

### Üretim Planlama Algoritmaları
- **Kapasite Optimizasyonu**: Günlük kapasite limitlerine göre otomatik planlama
- **Bağımlılık Analizi**: İş emirleri arası bağımlılıkları dikkate alan planlama
- **Malzeme Hazır Tarihi Entegrasyonu**: Satın alma modülü ile entegre planlama
- **Overflow Management**: Kapasite aşımında sonraki günlere akıllı dağıtım

### MRP Algoritması
- `calculate_materials()` fonksiyonu recursive BOM çözümü yapar
- Çok seviyeli ürün ağaçlarını destekler
- Ara ürünleri otomatik olarak hammaddelere kadar açar
- Malzeme ihtiyaçlarını toplar ve birleştirir

### Admin Özelleştirmeleri
- **Görsel İş Akışı Editörü**: Custom template ile drag&drop arayüz
- **Üretim Planlama Gantt**: Tam özellikli drag&drop planlama arayüzü
- **AJAX Workflow Kaydetme**: Gerçek zamanlı workflow kaydetme
- **Smart Form Filtering**: İş emri formlarında akıllı filtreleme
- **Custom Templates**: Zengin kullanıcı deneyimi için özel template'ler

### API Katmanı
- Django REST Framework kullanılıyor
- Serializer'lar hazır ancak frontend henüz yok
- Gelecekte React/Vue.js frontend planlanıyor

## 🔧 Geliştirme Komutları

```bash
# Yeni migration oluştur
python manage.py makemigrations

# Migration'ları uygula
python manage.py migrate

# Admin kullanıcısı oluştur
python manage.py createsuperuser

# Shell'de test
python manage.py shell

# Statik dosyaları topla (production için)
python manage.py collectstatic
```

## 📝 Kod Konvansiyonları
- Model isimleri: Türkçe (Musteri, Urun, Siparis)
- Field isimleri: Türkçe snake_case (musteri_adi, olusturulma_tarihi)
- Verbose_name: Türkçe UI metinleri
- Admin customization: Türkçe arayüz
- Docstring'ler: Türkçe açıklamalar

### 🔧 Çözülen Teknik Sorunlar (22 Ağustos 2025)
- **Unicode encoding hatası**: Print statement'larındaki Türkçe karakterler (cp1252 codec) ✅
- **MalzemeGelis veritabanı hatası**: Boş tablo durumunda exception handling ✅
- **Format_html hatası**: SafeString format code sorunu düzeltildi ✅
- **İş emri bağımlılık sorunu**: Akıllı filtreleme ile çözüldü ✅
- **Malzeme-operasyon eşleştirme sorunu**: Görsel drag&drop sistemi ile çözüldü ✅
- **Sipariş durum güncelleme sorunu**: İş emri oluşturma action'ında düzeltildi ✅
- **Encoding hatası görsel tasarımda**: Backend log mesajları temizlendi ✅

### 🔧 Çözülen Teknik Sorunlar (22 Ağustos 2025) - Üretim Planlama Gantt
- **Drag&Drop İşlemleri**: JavaScript syntax hatalar düzeltildi (duplicate variable declarations) ✅
- **Unplan Dropzone Görselleştirme**: Pointer-events sorunu çözüldü ✅
- **Çalışma Saati Sistemi**: Station-wide'dan cell-specific (station+date) sisteme geçiş ✅
- **Türkçe Decimal Format**: Süre parsing'inde virgül desteği (6,0h → 6.0) ✅
- **Kapasite Aşımı Tespiti**: Dataset.duration eksikliği sorunu çözüldü ✅
- **Overflow Handling**: Sonraki güne taşıma konfirmasyon sistemi çalışıyor ✅
- **Capacity Recalculation**: Çalışma saati değişikliklerinde otomatik yeniden hesaplama ✅

## 🚫 Bilinen Sınırlamalar
- Frontend arayüzü yok (sadece Django Admin)
- Gerçek zamanlı stok takibi eksik (üretim sürecinde güncellenecek)
- ~~Üretim modülü henüz geliştirilmedi~~ → **✅ Üretim modülü tamamlandı**
- ~~Malzeme-operasyon eşleştirme manuel~~ → **✅ Görsel eşleştirme sistemi eklendi**
- ~~Üretim planlama sistemi yok~~ → **✅ Gantt bazlı drag&drop planlama sistemi eklendi**

## 📋 Gelecek Özellikler (Roadmap)
1. **Üretim Takip Sistemi**: Gerçek zamanlı üretim durumu takibi
2. **Stok Hareket Modülü**: Gerçek zamanlı stok güncellemeleri ve hareket geçmişi
3. **Kapasite Planlama**: Makine ve insan kaynağı kapasitesi planlama
4. **Frontend Web Arayüzü**: React/Vue.js ile modern web arayüzü
5. **Mobile App**: Üretim katı ve depo için mobile uygulama
6. **API Entegrasyonu**: ERP sistemleri ile entegrasyon
7. **Kalite Kontrol Modülü**: Malzeme gelişinde kalite onay süreçleri
8. **Dashboard ve Analytics**: Üretim performans dashboard'ları

## 🎯 Öncelikli Geliştirme Alanları
1. **Üretim Takibi**: İş emirlerinin gerçek zamanlı durumu
2. **Stok Otomasyonu**: Üretim tamamlandığında otomatik stok güncellemesi
3. **Kapasite Yönetimi**: İstasyon kapasitelerine göre planlama
4. **Performans Analytics**: Üretim verimliliği raporları

---
*Son güncelleme: 2025-08-22 - Üretim Planlama Gantt Drag&Drop Sistemi Tamamen Çalışır Duruma Getirildi ✅*
*Claude Code session'ları için hazırlanmıştır*

## 📁 Backup Dosyaları
- `CLAUDE_backup_20250821_1155.md` - Malzeme Geliş sistemi tamamlandıktan sonraki durum
- `CLAUDE_backup_20250821_1647.md` - Üretim Modülü ve Görsel İş Akışı Tasarımı tamamlandıktan sonraki durum
- `CLAUDE_backup_20250821_1655.md` - Üretim Modülü tamamen stabil ve test edilmiş durumda
- `CLAUDE_backup_20250822.md` - **EN SON** - Üretim Planlama Gantt sistemi tamamen çalışır durumda