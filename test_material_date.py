import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import IsEmri

print("=== IS EMRI MALZEME TARIHLERI TEST ===")

# Tüm iş emirlerini al
is_emirleri = IsEmri.objects.all()
print(f"Toplam is emri: {is_emirleri.count()}")

for emri in is_emirleri:
    if emri.operasyon and 'sargı' in emri.operasyon.operasyon_adi.lower():
        print(f"\n--- {emri.operasyon.operasyon_adi} ---")
        print(f"Siparis: {emri.siparis_kalemi.siparis.id if emri.siparis_kalemi else 'None'}")
        
        # Malzeme hazır tarihini hesapla (debug çıktıları ile)
        malzeme_tarihi = emri.hesapla_malzeme_hazir_tarihi()
        print(f"Hesaplanan malzeme tarihi: {malzeme_tarihi}")
        print("=" * 50)