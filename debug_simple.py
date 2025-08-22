import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import SatinAlmaSiparisi, SatinAlmaKalemi, MalzemeIhtiyac

print("SIPARIS TARIHLERI:")
for siparis in SatinAlmaSiparisi.objects.all():
    print(f"ID: {siparis.id}, Durum: '{siparis.durum}', Teslim: {siparis.teslim_tarihi}, Guncel: {siparis.guncel_teslim_tarihi}")

print("\nKALEM - IHTIYAC ESLESTIRMELERI:")
for kalem in SatinAlmaKalemi.objects.all():
    if kalem.malzeme_ihtiyaci:
        print(f"Kalem {kalem.id}: Siparis {kalem.siparis.id}, Guncel Teslim: {kalem.siparis.guncel_teslim_tarihi}")
    else:
        print(f"Kalem {kalem.id}: MalzemeIhtiyaci yok")

print("\nFILTRE TEST:")
# Bekliyor durumundaki siparişlerin kalemlerini bul
kalemler = SatinAlmaKalemi.objects.filter(
    siparis__durum__in=['bekliyor', 'onaylandi', 'gonderildi']
)
print(f"Bekliyor/onaylandi/gonderildi durumundaki kalemler: {kalemler.count()}")
for k in kalemler:
    final_tarih = k.siparis.guncel_teslim_tarihi or k.siparis.teslim_tarihi
    print(f"  - Final tarih: {final_tarih}")