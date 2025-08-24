# backend/production/serializers.py

from rest_framework import serializers
from .models import Musteri, Urun, Siparis, SiparisKalem, SiparisDosya



class MusteriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musteri
        fields = '__all__'
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']


class UrunSerializer(serializers.ModelSerializer):
    stok_durumu = serializers.ReadOnlyField()
    
    class Meta:
        model = Urun
        fields = '__all__'
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi', 'stok_durumu']

class SiparisKalemSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.ad', read_only=True)
    toplam_tutar = serializers.SerializerMethodField()
    
    class Meta:
        model = SiparisKalem
        fields = [
            'id', 'urun', 'urun_adi', 'miktar', 'birim_fiyat', 
            'doviz', 'kur', 'birim_fiyat_usd', 'teslim_tarihi', 
            'son_kullanici_ulke', 'toplam_tutar', 'notlar'
        ]
    
    def get_toplam_tutar(self, obj):
        """USD cinsinden toplam tutarı hesapla"""
        if obj.birim_fiyat_usd:
            return obj.miktar * obj.birim_fiyat_usd
        return 0


class SiparisDosyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiparisDosya
        fields = ['id', 'dosya', 'aciklama', 'yuklenme_tarihi']


class SiparisSerializer(serializers.ModelSerializer):
    musteri_adi = serializers.CharField(source='musteri.ad', read_only=True)
    kalemler = SiparisKalemSerializer(many=True, read_only=True)
    dosyalar = SiparisDosyaSerializer(many=True, read_only=True)
    toplam_tutar = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Siparis
        fields = [
            'id', 'siparis_no', 'musteri', 'musteri_adi', 'tarih', 
            'durum', 'musteri_ulke', 
            'notlar', 'siparis_mektubu', 'maliyet_hesabi', 'dosya', 
            'kalemler', 'dosyalar', 'toplam_tutar', 
            'olusturulma_tarihi', 'guncellenme_tarihi'
        ]

class SiparisCreateSerializer(serializers.ModelSerializer):
    kalemler = serializers.CharField() # JSON string olarak alacak
    
    class Meta:
        model = Siparis
        fields = ['id', 'siparis_no', 'musteri', 'tarih', 'durum', 'musteri_ulke', 'notlar', 'siparis_mektubu', 'maliyet_hesabi', 'dosya', 'kalemler']
    
    def create(self, validated_data):
        import json
        
        # Kalemler JSON string olarak geliyor, parse et
        kalemler_json = validated_data.pop('kalemler', '[]')
        if isinstance(kalemler_json, str):
            kalemler_data = json.loads(kalemler_json)
        else:
            kalemler_data = kalemler_json
            
        siparis = Siparis.objects.create(**validated_data)
        
        for kalem_data in kalemler_data:
            # Urun ID'sini integer'a çevir ve Urun nesnesini al
            if 'urun' in kalem_data:
                from .models import Urun
                urun_id = int(kalem_data['urun'])
                kalem_data['urun'] = Urun.objects.get(id=urun_id)
            
            SiparisKalem.objects.create(siparis=siparis, **kalem_data)
        
        return siparis