import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import SatinAlmaSiparisi, SatinAlmaKalemi

print("=== SATINALMA SIPARIS DURUMLAR ===")
for s in SatinAlmaSiparisi.objects.all():
    print(f"Siparis ID: {s.id}, Durum: '{s.durum}', Tarih: {s.teslim_tarihi}")

print("\n=== SATINALMA KALEMLERI ===") 
for k in SatinAlmaKalemi.objects.all():
    print(f"Kalem ID: {k.id}, Siparis Durumu: '{k.siparis.durum}', MalzemeIhtiyaci: {k.malzeme_ihtiyaci}")
    
print("\n=== PROBLEM TESPIT ===")
# Hangi durumları filtreliyoruz
filtre_durumlari = ['onaylandi', 'gonderildi']
print(f"Aranan durumlar: {filtre_durumlari}")

# Bu durumlarla eşleşen siparişler var mı
eslesen = SatinAlmaSiparisi.objects.filter(durum__in=filtre_durumlari)
print(f"Eslesen siparis sayisi: {eslesen.count()}")