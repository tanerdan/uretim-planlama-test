# 🧪 Üretim Planlama Sistemi - Kullanıcı Test Rehberi

## 🚀 Hızlı Başlangıç (5 Dakikada Test Etmeye Hazır!)

### ⚡ **Ön Koşullar**
- Python 3.8+ yüklü olmalı
- Node.js 16+ yüklü olmalı

### 📋 **Adım 1: Projeyi İndir**
```bash
# Proje klasörüne git
cd D:\Documents_D\SoftwareDevelopment\uretim-planlama
```

### 🔧 **Adım 2: Backend Hazırla (2 dakika)**
```bash
# Virtual environment aktifleştir
venv\Scripts\activate

# Gerekli paketleri yükle (sadece ilk seferde)
pip install -r requirements.txt

# Veritabanını hazırla (sadece ilk seferde)
python manage.py migrate

# Test admin kullanıcısı oluştur
python manage.py createsuperuser
# Kullanıcı adı: admin
# Email: admin@test.com  
# Şifre: admin123

# Backend sunucuyu başlat
python manage.py runserver 8000
```

### 🌐 **Adım 3: Frontend Hazırla (1 dakika)**
```bash
# Yeni terminal aç ve frontend klasörüne git  
cd frontend

# Node paketlerini yükle (sadece ilk seferde)
npm install

# Frontend sunucuyu başlat
npm run dev
```

## 🎯 **Test Erişim Noktaları**

### 📊 **1. Django Admin Panel** ⭐⭐⭐ (Ana Test Alanı)
- **URL**: http://127.0.0.1:8000/admin/
- **Giriş**: admin / admin123
- **Test Edilecek Modüller**:
  - ✅ Müşteri Yönetimi
  - ✅ Ürün Yönetimi (BOM dahil)
  - ✅ Sipariş Yönetimi
  - ✅ MRP - Malzeme Planlama
  - ✅ Satın Alma Modülü
  - ✅ Malzeme Geliş Takibi
  - ✅ **Üretim Modülü** (İş istasyonları, akışlar, emirler)
  - ✅ **Görsel İş Akışı Tasarımı** (Drag&Drop)

### 🌟 **2. React Web Arayüzü** ⭐⭐ (Modern UI)
- **URL**: http://localhost:5173/
- **Test Edilecek Özellikler**:
  - ✅ Sipariş Listesi ve Filtreleme
  - ✅ Yeni Sipariş Oluşturma
  - ✅ Dosya Upload (3 tip dosya)
  - ✅ Çoklu Para Birimi (USD, EUR, TRY, GBP)
  - ✅ Gerçek Zamanlı Kur Hesaplama

### 🔗 **3. API Endpoints** ⭐ (Geliştiriciler İçin)
- **Base URL**: http://127.0.0.1:8000/api/
- **Test**: http://127.0.0.1:8000/api/siparis/ (Siparişler)

## 📝 **Test Senaryoları**

### 🏗️ **Senaryo 1: Temel Veri Girişi (15 dakika)**
1. **Admin Panel'e giriş yap**
2. **Müşteri ekle**: 
   - ACME Corp, Türkiye, aktif durum
3. **Hammadde ürünleri ekle**:
   - Çelik Plaka (kg), Vida M8 (adet), Boya (litre)
4. **Bitmiş ürün ekle**:
   - Masa (adet) - BOM ile hammadde bağla
5. **Sipariş oluştur**:
   - ACME Corp'tan 10 adet masa siparişi

### ⚙️ **Senaryo 2: MRP Süreci (10 dakika)**
1. **MRP Modülü'ne git** (Production → Malzeme planlaması)
2. **Sipariş seç** ve "Malzeme İhtiyacını Hesapla"
3. **Sonuçları incele**: BOM'a göre malzeme ihtiyaçları
4. **Satın alma siparişi oluştur**

### 🏭 **Senaryo 3: Üretim Planlama (20 dakika)**
1. **İş İstasyonları tanımla**:
   - Kesim Tezgahı, Montaj Masası
2. **İş Akışı oluştur**:
   - Masa ürünü için: Kesim → Montaj
3. **Görsel Tasarım kullan**:
   - Drag&drop ile operasyonları tasarla
   - Malzemeleri operasyonlara ata
4. **İş Emri oluştur**:
   - Siparişten iş emri oluştur

### 🌐 **Senaryo 4: Modern Web Arayüzü (10 dakika)**
1. **React arayüzüne git** (http://localhost:5173)
2. **Yeni sipariş oluştur**:
   - Müşteri seç, ürün ekle, para birimi değiştir
3. **Dosya yükle**:
   - Sipariş mektubu, maliyet hesabı upload et
4. **Sipariş listesini incele**:
   - Filtreleme, arama, USD değerleri

## 🐛 **Bilinen Test Limitasyonları**
- Gerçek zamanlı stok takibi henüz yok
- Üretim operasyonları manuel durumda
- Kapasite planlama algoritması geliştirilmemiş

## 📞 **Test Feedback'i**
Test sırasında karşılaştığınız sorunları ve önerileri not alın:
- ✅ **Çalışan özellikler**
- ❌ **Sorunlu alanlar** 
- 💡 **İyileştirme önerileri**

---

## 🎯 **Hızlı Demo İçin Öncelikli Test Alanları**

### ⭐⭐⭐ **Mutlaka Test Et**:
1. **MRP Sistemi** - Malzeme planlama ve otomatik hesaplama
2. **Görsel İş Akışı** - Drag&drop ile üretim süreci tasarımı
3. **React Sipariş Modülü** - Modern web arayüzü

### ⭐⭐ **İkinci Öncelik**:
1. Satın alma süreçleri
2. Malzeme geliş takibi
3. Dosya upload sistemi

### ⭐ **Opsiyonel**:
1. API endpoint testleri
2. Admin panel özelleştirmeleri

**Test süresi**: Temel demo için **30-45 dakika** yeterli
**Detaylı test**: **2-3 saat** 

Bu rehber ile sistemi hızlıca test edebilir ve geri bildirim verebilirsiniz! 🚀