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
    toplam_fiyat = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = SiparisKalem
        fields = ['id', 'urun', 'urun_adi', 'miktar', 'birim_fiyat', 'toplam_fiyat', 'notlar']


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
            'teslim_tarihi', 'durum', 'notlar', 'dosya', 'kalemler', 
            'dosyalar', 'toplam_tutar', 'olusturulma_tarihi', 'guncellenme_tarihi'
        ]

class SiparisCreateSerializer(serializers.ModelSerializer):
    kalemler = SiparisKalemSerializer(many=True)
    
    class Meta:
        model = Siparis
        fields = ['siparis_no', 'musteri', 'tarih', 'teslim_tarihi', 'durum', 'notlar', 'dosya', 'kalemler']
    
    def create(self, validated_data):
        kalemler_data = validated_data.pop('kalemler')
        siparis = Siparis.objects.create(**validated_data)
        
        for kalem_data in kalemler_data:
            SiparisKalem.objects.create(siparis=siparis, **kalem_data)
        
        return siparis