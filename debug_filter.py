import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import MalzemeIhtiyac, SatinAlmaKalemi

print("=== SIPARIS SIP-20250819-185314 ICIN IHTIYACLAR ===")
for ihtiyac in MalzemeIhtiyac.objects.all():
    if 'SIP-20250819-185314' in str(ihtiyac.ilgili_siparisler):
        print(f"ID: {ihtiyac.id}")
        # Malzeme adının ilk 30 karakterini al
        try:
            malzeme_adi = str(ihtiyac.malzeme_adi)
            print(f"Malzeme (ilk 30 kar): {malzeme_adi[:30]}...")
        except:
            print("Malzeme: [Encoding Error]")

print("\n=== SATINALMA KALEMLERI ===")
for kalem in SatinAlmaKalemi.objects.all():
    print(f"Kalem {kalem.id}:")
    print(f"  MalzemeIhtiyaci ID: {kalem.malzeme_ihtiyaci.id if kalem.malzeme_ihtiyaci else None}")
    if kalem.malzeme_ihtiyaci:
        try:
            malzeme_adi = str(kalem.malzeme_ihtiyaci.malzeme_adi)
            print(f"  Malzeme (ilk 30 kar): {malzeme_adi[:30]}...")
        except:
            print("  Malzeme: [Encoding Error]")

print("\n=== FILTER TESTI ===")
# Manuel olarak filtre testi
test_ihtiyac_ids = [1, 2]  # Kalemlerle ilişkili olan ID'ler
for test_id in test_ihtiyac_ids:
    try:
        ihtiyac = MalzemeIhtiyac.objects.get(id=test_id)
        malzeme_adi = str(ihtiyac.malzeme_adi)
        
        print(f"\nTest ID {test_id}:")
        print(f"Malzeme adi: {malzeme_adi[:30]}...")
        
        # Bu malzeme adı ile kalem arama
        kalemler = SatinAlmaKalemi.objects.filter(
            malzeme_ihtiyaci__malzeme_adi=malzeme_adi
        )
        print(f"Bulunan kalem sayisi: {kalemler.count()}")
        
        # Durumla da filtrele
        kalemler_durumlu = SatinAlmaKalemi.objects.filter(
            malzeme_ihtiyaci__malzeme_adi=malzeme_adi,
            siparis__durum__in=['bekliyor', 'onaylandi', 'gonderildi']
        )
        print(f"Durum filtreli kalem sayisi: {kalemler_durumlu.count()}")
        
    except Exception as e:
        print(f"Test ID {test_id} error: {e}")