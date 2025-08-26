# backend/production/serializers.py

from rest_framework import serializers
from .models import (
    Musteri, Urun, Siparis, SiparisKalem, SiparisDosya,
    IsIstasyonu, StandardIsAdimi, IsAkisi, IsAkisiOperasyon, IsEmri, UrunRecete, BOMTemplate
)



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
            'durum', 'musteri_ulke', 'son_kullanici_ulke',
            'notlar', 'siparis_mektubu', 'maliyet_hesabi', 'dosya', 
            'kalemler', 'dosyalar', 'toplam_tutar', 
            'olusturulma_tarihi', 'guncellenme_tarihi'
        ]

class SiparisCreateSerializer(serializers.ModelSerializer):
    kalemler = serializers.CharField() # JSON string olarak alacak
    
    class Meta:
        model = Siparis
        fields = ['id', 'siparis_no', 'musteri', 'tarih', 'durum', 'musteri_ulke', 'son_kullanici_ulke', 'notlar', 'siparis_mektubu', 'maliyet_hesabi', 'dosya', 'kalemler']
    
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

    def update(self, instance, validated_data):
        import json
        
        # Kalemler JSON string olarak geliyor, parse et
        kalemler_json = validated_data.pop('kalemler', None)
        if kalemler_json:
            if isinstance(kalemler_json, str):
                kalemler_data = json.loads(kalemler_json)
            else:
                kalemler_data = kalemler_json
            
            # Mevcut kalemleri sil
            instance.kalemler.all().delete()
            
            # Yeni kalemleri oluştur
            for kalem_data in kalemler_data:
                # Urun ID'sini integer'a çevir ve Urun nesnesini al
                if 'urun' in kalem_data:
                    from .models import Urun
                    urun_id = int(kalem_data['urun'])
                    kalem_data['urun'] = Urun.objects.get(id=urun_id)
                
                SiparisKalem.objects.create(siparis=instance, **kalem_data)
        
        # Sipariş bilgilerini güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


# Production Serializers

class IsIstasyonuSerializer(serializers.ModelSerializer):
    """İş İstasyonu Serializer"""
    durum_display = serializers.CharField(source='get_durum_display', read_only=True)
    tip_display = serializers.CharField(source='get_tip_display', read_only=True)
    
    class Meta:
        model = IsIstasyonu
        fields = '__all__'
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']


class StandardIsAdimiSerializer(serializers.ModelSerializer):
    """Standard İş Adımı Serializer"""
    kategori_display = serializers.CharField(source='get_kategori_display', read_only=True)
    
    class Meta:
        model = StandardIsAdimi
        fields = '__all__'
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']


class IsAkisiOperasyonSerializer(serializers.ModelSerializer):
    """İş Akışı Operasyon Serializer"""
    istasyon_adi = serializers.CharField(source='istasyon.ad', read_only=True)
    standard_is_adimi_adi = serializers.CharField(source='standard_is_adimi.ad', read_only=True)
    
    class Meta:
        model = IsAkisiOperasyon
        fields = '__all__'


class IsAkisiSerializer(serializers.ModelSerializer):
    """İş Akışı Serializer"""
    operasyonlar = IsAkisiOperasyonSerializer(many=True, read_only=True)
    operasyon_sayisi = serializers.SerializerMethodField()
    urun_adi = serializers.CharField(source='urun.ad', read_only=True)
    
    class Meta:
        model = IsAkisi
        fields = '__all__'
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']
    
    def get_operasyon_sayisi(self, obj):
        return obj.operasyonlar.count()


class IsEmriSerializer(serializers.ModelSerializer):
    """İş Emri Serializer"""
    durum_display = serializers.CharField(source='get_durum_display', read_only=True)
    istasyon_adi = serializers.CharField(source='istasyon.ad', read_only=True)
    urun_adi = serializers.CharField(source='urun.ad', read_only=True)
    siparis_no = serializers.CharField(source='siparis.siparis_no', read_only=True)
    musteri_adi = serializers.CharField(source='siparis.musteri.ad', read_only=True)
    
    class Meta:
        model = IsEmri
        fields = '__all__'
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']


class UrunReceteSerializer(serializers.ModelSerializer):
    """Ürün Reçetesi (BOM) Serializer"""
    urun_adi = serializers.CharField(source='urun.ad', read_only=True)
    malzeme_adi = serializers.CharField(source='malzeme.ad', read_only=True)
    malzeme_kod = serializers.CharField(source='malzeme.kod', read_only=True)
    malzeme_birim = serializers.CharField(source='malzeme.birim', read_only=True)
    malzeme_kategori = serializers.CharField(source='malzeme.get_kategori_display', read_only=True)
    malzeme_stok_durumu = serializers.CharField(source='malzeme.stok_durumu', read_only=True)
    
    class Meta:
        model = UrunRecete
        fields = [
            'id', 'urun', 'malzeme', 'miktar', 'notlar',
            'urun_adi', 'malzeme_adi', 'malzeme_kod', 'malzeme_birim', 
            'malzeme_kategori', 'malzeme_stok_durumu'
        ]


class BOMTemplateSerializer(serializers.ModelSerializer):
    """BOM Template Serializer"""
    eslestirilen_urun_adi = serializers.CharField(source='eslestirilen_urun.ad', read_only=True)
    missing_dependencies = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    hierarchical_structure = serializers.SerializerMethodField()
    
    class Meta:
        model = BOMTemplate
        fields = [
            'id', 'bom_tanimi', 'aciklama', 'malzemeler', 'eslestirilen_urun', 
            'eslestirilen_urun_adi', 'olusturulma_tarihi', 'guncellenme_tarihi',
            'missing_dependencies', 'is_complete', 'hierarchical_structure'
        ]
        read_only_fields = ['olusturulma_tarihi', 'guncellenme_tarihi', 'missing_dependencies', 'is_complete']
    
    
    def get_missing_dependencies(self, obj):
        return obj.get_missing_dependencies()
    
    def get_is_complete(self, obj):
        return obj.is_complete()
    
    def get_hierarchical_structure(self, obj):
        return obj.get_hierarchical_structure()