import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import MalzemeIhtiyac, SatinAlmaKalemi

print("=== SPECIFIC TEST ===")

# MalzemeIhtiyaci ID 2 (kalem 1 ile ilişkili)
try:
    ihtiyac_2 = MalzemeIhtiyac.objects.get(id=2)
    print(f"MalzemeIhtiyaci 2 siparisler: {ihtiyac_2.ilgili_siparisler}")
    
    # Bu ihtiyacın malzeme adı ile kalem ara
    kalemler = SatinAlmaKalemi.objects.filter(malzeme_ihtiyaci=ihtiyac_2)
    print(f"ID 2 ile direkt ilişkili kalem sayısı: {kalemler.count()}")
    
    # Malzeme adı filtresi ile ara
    kalemler_adi = SatinAlmaKalemi.objects.filter(
        malzeme_ihtiyaci__malzeme_adi=ihtiyac_2.malzeme_adi
    )
    print(f"Malzeme adı ile bulunan kalem sayısı: {kalemler_adi.count()}")
    
    # Durum filtresi ekle
    kalemler_durum = SatinAlmaKalemi.objects.filter(
        malzeme_ihtiyaci__malzeme_adi=ihtiyac_2.malzeme_adi,
        siparis__durum__in=['bekliyor', 'onaylandi', 'gonderildi']
    )
    print(f"Durum filtreli kalem sayısı: {kalemler_durum.count()}")
    
    if kalemler_durum.exists():
        kalem = kalemler_durum.first()
        tarih = kalem.siparis.guncel_teslim_tarihi or kalem.siparis.teslim_tarihi
        print(f"Bulunan kalem tarihi: {tarih}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n=== ENCODING SAFE TEST ===")
# Unicode olmadan sadece sayısal karşılaştırma
for kalem in SatinAlmaKalemi.objects.all():
    print(f"Kalem {kalem.id}: MalzemeIhtiyaci {kalem.malzeme_ihtiyaci.id}")
    print(f"  Siparis durum: {kalem.siparis.durum}")
    print(f"  Guncel teslim: {kalem.siparis.guncel_teslim_tarihi}")
    print(f"  Normal teslim: {kalem.siparis.teslim_tarihi}")
    final_tarih = kalem.siparis.guncel_teslim_tarihi or kalem.siparis.teslim_tarihi
    print(f"  Final tarih: {final_tarih}")
    print()