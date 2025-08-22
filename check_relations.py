import os
import django
import sys
sys.path.append('backend')
os.chdir('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uretim_planlama.settings')
django.setup()

from production.models import *

# MalzemeIhtiyac kayıtlarını kontrol et
print('=== MALZEME İHTİYAÇ KAYITLARI ===')
ihtiyaclar = MalzemeIhtiyac.objects.all()
print(f'Toplam MalzemeIhtiyac: {ihtiyaclar.count()}')
for i in ihtiyaclar[:5]:
    print(f'- {i.malzeme_adi}: {i.miktar} {i.birim}')

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
print('=== ÖRNEK MALZEME KONTROLÜ ===')
# Trafo Yağı için kontrol
trafo_ihtiyaclari = MalzemeIhtiyac.objects.filter(malzeme_adi__icontains='Trafo')
print(f'Trafo ihtiyaçları: {trafo_ihtiyaclari.count()}')
for t in trafo_ihtiyaclari:
    print(f'- {t.malzeme_adi} (ID: {t.id})')
    
# Bu malzeme için satın alma kalemleri var mı?
trafo_kalemleri = SatinAlmaKalemi.objects.filter(malzeme_ihtiyaci__malzeme_adi__icontains='Trafo')
print(f'Trafo için SatinAlmaKalemi: {trafo_kalemleri.count()}')

print()
print('=== TÜM SATINALma SiPARİŞLERİ ===')
siparisler = SatinAlmaSiparisi.objects.all()
print(f'Toplam SatinAlmaSiparisi: {siparisler.count()}')
for s in siparisler:
    print(f'- {s.siparis_no}: {s.tedarikci} - {s.durum}')