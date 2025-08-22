import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from backend.production.models import IsEmri

# Debug print'leri kaldırıp fonksiyonu test et
emri = IsEmri.objects.first()
if emri:
    print("Test emri bulundu")
    print(f"Siparis kalemi var: {emri.siparis_kalemi is not None}")
    if emri.siparis_kalemi:
        print(f"Siparis ID: {emri.siparis_kalemi.siparis.id}")
    
    # Malzeme tarihini hesapla
    tarih = emri.hesapla_malzeme_hazir_tarihi()
    print(f"Hesaplanan tarih: {tarih}")
else:
    print("Is emri bulunamadi")