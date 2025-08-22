import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import SatinAlmaSiparisi, SatinAlmaKalemi, MalzemeIhtiyac

print("=== SATINALMA SIPARIS VE KALEMLERI ===")
for siparis in SatinAlmaSiparisi.objects.all():
    print(f"Siparis ID: {siparis.id}")
    print(f"  Durum: '{siparis.durum}'")
    print(f"  Teslim Tarihi: {siparis.teslim_tarihi}")
    print(f"  Guncel Teslim Tarihi: {siparis.guncel_teslim_tarihi}")
    print(f"  Kalemler:")
    
    for kalem in SatinAlmaKalemi.objects.filter(siparis=siparis):
        print(f"    - Kalem ID: {kalem.id}")
        if kalem.malzeme_ihtiyaci:
            print(f"      Malzeme: {kalem.malzeme_ihtiyaci.malzeme_adi}")
        else:
            print(f"      Malzeme: None")
    print()

print("=== MALZEME IHTIYACLARI ===")
for ihtiyac in MalzemeIhtiyac.objects.all():
    print(f"Ihtiyac ID: {ihtiyac.id}")
    print(f"  Malzeme: {ihtiyac.malzeme_adi}")
    print(f"  Ilgili Siparisler: {ihtiyac.ilgili_siparisler}")
    print()

print("=== MALZEME ESLESTIRME TESTI ===")
# AG sargı ve YG sargı için test
aranan_malzemeler = ['AG Sargı', 'YG Sargı']
for malzeme in aranan_malzemeler:
    print(f"\n--- {malzeme} için ---")
    
    # Bu malzeme adında ihtiyaç var mı?
    ihtiyaclar = MalzemeIhtiyac.objects.filter(malzeme_adi__icontains=malzeme.split()[0])
    print(f"Bulunan ihtiyaclar: {ihtiyaclar.count()}")
    for i in ihtiyaclar:
        print(f"  - {i.malzeme_adi}")
    
    # Bu malzeme için satın alma kalemi var mı?
    kalemler = SatinAlmaKalemi.objects.filter(
        malzeme_ihtiyaci__malzeme_adi__icontains=malzeme.split()[0]
    )
    print(f"Bulunan kalemler: {kalemler.count()}")
    for k in kalemler:
        print(f"  - Siparis Durum: {k.siparis.durum}")
        print(f"  - Teslim: {k.siparis.teslim_tarihi}")
        print(f"  - Guncel Teslim: {k.siparis.guncel_teslim_tarihi}")