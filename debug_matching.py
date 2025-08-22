import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import MalzemeIhtiyac, SatinAlmaKalemi

print("=== MALZEME IHTIYACLARI ===")
for ihtiyac in MalzemeIhtiyac.objects.all():
    print(f"ID: {ihtiyac.id}")
    print(f"Siparisler: {ihtiyac.ilgili_siparisler}")
    # Unicode sorunu için malzeme adını kısalt
    malzeme = str(ihtiyac.malzeme_adi)[:20] + "..." if len(str(ihtiyac.malzeme_adi)) > 20 else str(ihtiyac.malzeme_adi)
    try:
        print(f"Malzeme: {malzeme}")
    except:
        print("Malzeme: [Unicode Error]")
    print()

print("=== SATINALMA KALEMLERI ===")  
for kalem in SatinAlmaKalemi.objects.all():
    print(f"Kalem ID: {kalem.id}")
    print(f"MalzemeIhtiyaci: {kalem.malzeme_ihtiyaci}")
    if kalem.malzeme_ihtiyaci:
        try:
            malzeme = str(kalem.malzeme_ihtiyaci.malzeme_adi)[:20]
            print(f"Malzeme: {malzeme}...")
        except:
            print("Malzeme: [Unicode Error]")
    print()

print("=== ESLESTIRME TESTI ===")
# Siparis 2 ile ilgili malzeme ihtiyaçlarını bul
siparis_2_ihtiyaclari = []
for ihtiyac in MalzemeIhtiyac.objects.all():
    if '2' in str(ihtiyac.ilgili_siparisler):
        siparis_2_ihtiyaclari.append(ihtiyac)

print(f"Siparis 2 icin ihtiyac sayisi: {len(siparis_2_ihtiyaclari)}")

# Bu ihtiyaçlar için satın alma kalemleri var mı?
for ihtiyac in siparis_2_ihtiyaclari[:3]:  # Sadece ilk 3'ü test et
    try:
        malzeme_adi = str(ihtiyac.malzeme_adi)
        print(f"\n{malzeme_adi[:20]}... icin:")
        
        # Bu malzeme adı ile eşleşen kalemler
        kalemler = SatinAlmaKalemi.objects.filter(
            malzeme_ihtiyaci__malzeme_adi=malzeme_adi,
            siparis__durum__in=['bekliyor', 'onaylandi', 'gonderildi']
        )
        print(f"  Bulunan kalem sayisi: {kalemler.count()}")
        
    except Exception as e:
        print(f"  Error: {e}")