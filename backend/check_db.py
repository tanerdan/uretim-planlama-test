#!/usr/bin/env python
import os
import django
import sys

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uretim_planlama.settings')
django.setup()

from production.models import *

# MalzemeIhtiyac kayıtlarını kontrol et
print('=== MALZEME İHTİYAÇ KAYITLARI ===')
ihtiyaclar = MalzemeIhtiyac.objects.all()
print(f'Toplam MalzemeIhtiyac: {ihtiyaclar.count()}')
for i in ihtiyaclar[:5]:
    print(f'- {i.malzeme_adi}: {i.miktar} {i.birim} (Durum: {i.durum})')

print()
print('=== SATIN ALMA KAYITLARI ===')
satinalma_kalemleri = SatinAlmaKalemi.objects.all()
print(f'Toplam SatinAlmaKalemi: {satinalma_kalemleri.count()}')
for k in satinalma_kalemleri[:5]:
    malzeme_adi = k.malzeme_ihtiyaci.malzeme_adi if k.malzeme_ihtiyaci else "None"
    print(f'- Malzeme: {malzeme_adi}')

print()
print('=== İLİŞKİ KONTROLÜ ===')
# Malzeme ihtiyacına sahip olan satın alma kalemlerini bul
iliskili_kalemler = SatinAlmaKalemi.objects.filter(malzeme_ihtiyaci__isnull=False)
print(f'MalzemeIhtiyaci bağlı SatinAlmaKalemi: {iliskili_kalemler.count()}')

print()
print('=== DURUM ANALİZİ ===')
# Malzeme ihtiyaçlarının durumları
durum_sayilari = {}
for ihtiyac in ihtiyaclar:
    durum = ihtiyac.durum
    if durum not in durum_sayilari:
        durum_sayilari[durum] = 0
    durum_sayilari[durum] += 1

for durum, sayi in durum_sayilari.items():
    print(f'- {durum}: {sayi} adet')

print()
print('=== SATINALMA DURUMLARı ===')
siparisler = SatinAlmaSiparisi.objects.all()
print(f'Toplam SatinAlmaSiparisi: {siparisler.count()}')
siparis_durumlari = {}
for siparis in siparisler:
    durum = siparis.durum
    if durum not in siparis_durumlari:
        siparis_durumlari[durum] = 0
    siparis_durumlari[durum] += 1

for durum, sayi in siparis_durumlari.items():
    print(f'- {durum}: {sayi} adet')
    
# Önemli: Onaylanmış siparişler var mı?
onaylanmis = SatinAlmaSiparisi.objects.filter(durum__in=['onaylandi', 'gonderildi'])
print(f'Onaylanmış/Gönderilmiş siparişler: {onaylanmis.count()}')