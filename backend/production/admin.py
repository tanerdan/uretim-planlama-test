# backend/production/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.db import transaction, models
from django.db.models import Sum, F
from django import forms
from collections import defaultdict
import json

# Model import'ları
from .models import (
    Musteri, Urun, UrunRecete, Siparis, 
    SiparisKalem, SiparisDosya, MalzemeIhtiyac,
    Tedarikci, SatinAlmaSiparisi, SatinAlmaKalemi,
    SatinAlmaTeslimGuncelleme, MalzemeGelis, StandardIsAdimi,
    IsIstasyonu, IsAkisi, IsAkisiOperasyon, IsEmri
)

@admin.register(Musteri)
class MusteriAdmin(admin.ModelAdmin):
    list_display = ['kod', 'ad', 'telefon', 'email', 'aktif', 'olusturulma_tarihi']
    list_filter = ['aktif', 'olusturulma_tarihi']
    search_fields = ['ad', 'kod', 'email', 'telefon']
    readonly_fields = ['olusturulma_tarihi', 'guncellenme_tarihi']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('kod', 'ad', 'aktif')
        }),
        ('İletişim Bilgileri', {
            'fields': ('telefon', 'email', 'adres')
        }),
        ('Ek Bilgiler', {
            'fields': ('notlar',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )

class UrunReceteInline(admin.TabularInline):
    model = UrunRecete
    fk_name = 'urun'  # Hangi ForeignKey kullanılacağını belirtiyoruz
    extra = 1
    fields = ['malzeme', 'miktar', 'notlar']
    autocomplete_fields = ['malzeme']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Sadece hammadde ve ara ürünleri malzeme olarak göster"""
        if db_field.name == "malzeme":
            kwargs["queryset"] = Urun.objects.filter(kategori__in=['hammadde', 'ara_urun'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(UrunRecete)
class UrunReceteAdmin(admin.ModelAdmin):
    list_display = ['urun', 'malzeme', 'miktar', 'malzeme_birimi']
    list_filter = ['urun__kategori', 'malzeme__kategori']
    search_fields = ['urun__ad', 'malzeme__ad']
    autocomplete_fields = ['urun', 'malzeme']
    
    def malzeme_birimi(self, obj):
        return obj.malzeme.birim
    malzeme_birimi.short_description = 'Birim'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Form alanları için özel filtreler"""
        if db_field.name == "urun":
            # Sadece ara ürün ve bitmiş ürünler reçeteye sahip olabilir
            kwargs["queryset"] = Urun.objects.filter(kategori__in=['ara_urun', 'bitmis_urun'])
        elif db_field.name == "malzeme":
            # Sadece hammadde ve ara ürünler malzeme olabilir
            kwargs["queryset"] = Urun.objects.filter(kategori__in=['hammadde', 'ara_urun'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ['kod', 'ad', 'kategori', 'birim', 'stok_miktari', 'minimum_stok', 'stok_durumu', 'bom_goster', 'bom_detay']
    list_filter = ['kategori', 'birim'] 
    search_fields = ['ad', 'kod']
    ordering = ['kategori', 'ad'] 
    
    # Form düzeni
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('kod', 'ad', 'kategori', 'birim')
        }),
        ('Stok Bilgileri', {
            'fields': ('stok_miktari', 'minimum_stok')
        }),
    )
    
    def get_inlines(self, request, obj):
        inlines = []
        if obj and obj.kategori in ['ara_urun', 'bitmis_urun']:
            inlines.append(UrunReceteInline)
        return inlines
    
    def stok_durumu(self, obj):
        if obj.stok_miktari <= 0:
            return "❌ Stok Yok"
        elif obj.stok_miktari <= obj.minimum_stok:
            return "⚠️ Kritik"
        else:
            return "✅ Yeterli"
    stok_durumu.short_description = 'Stok Durumu'
    
    def bom_goster(self, obj):
        """BOM görüntüleme butonu"""
        if obj.kategori in ['ara_urun', 'bitmis_urun'] and obj.recete.exists():
            url = reverse('admin:production_urun_change', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background-color: #4CAF50; color: white; padding: 2px 10px; text-decoration: none; border-radius: 3px;">📋 BOM</a>',
                url
            )
        return "-"
    bom_goster.short_description = 'Reçete'
    
    def bom_detay(self, obj):
        """Hover ile detaylı BOM göster"""
        if obj.kategori in ['ara_urun', 'bitmis_urun'] and obj.recete.exists():
            bom_items = []
            
            for item in obj.recete.all():
                bom_items.append(
                    f'<li style="margin: 5px 0; padding: 3px 0;">'
                    f'<span style="color: #4CAF50; font-weight: bold;">✓</span> '
                    f'<strong>{item.miktar}</strong> {item.malzeme.birim} - {item.malzeme.ad} '
                    f'<span style="color: #666;">({item.malzeme.get_kategori_display()})</span></li>'
                )
            
            bom_html = f'''
            <div style="position: relative; display: inline-block;">
                <span style="cursor: pointer; color: #0066cc; font-weight: bold;" 
                      onmouseover="this.nextElementSibling.style.display='block'" 
                      onmouseout="this.nextElementSibling.style.display='none'">
                    📋 Reçete ({obj.recete.count()})
                </span>
                <div style="display: none; position: absolute; background-color: #f9f9f9; 
                           min-width: 350px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); 
                           padding: 15px; z-index: 1000; left: 0; top: 100%; margin-top: 5px; 
                           border-radius: 5px; border: 1px solid #ddd;">
                    <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 1px solid #ddd; 
                              padding-bottom: 5px;">🏭 {obj.ad} - Malzeme Listesi</h4>
                    <ul style="margin: 0; padding-left: 0; list-style-type: none;">
                        {"".join(bom_items)}
                    </ul>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; 
                               font-weight: bold; color: #666;">
                        Toplam {obj.recete.count()} farklı malzeme
                    </div>
                </div>
            </div>
            '''
            return format_html(bom_html)
        elif obj.kategori == 'hammadde':
            return format_html('<span style="color: #999;">Hammadde</span>')
        else:
            return format_html('<span style="color: #FF9800;">⚠️ Reçete yok</span>')
    bom_detay.short_description = 'Reçete Detay'
    
class SiparisKalemInline(admin.TabularInline):
    model = SiparisKalem
    extra = 1  # Boş form sayısı
    fields = ['urun', 'miktar', 'birim_fiyat', 'notlar']
    autocomplete_fields = ['urun']  # Ürün seçimi için otomatik tamamlama

class SiparisDosyaInline(admin.TabularInline):
    model = SiparisDosya
    extra = 1
    fields = ['dosya', 'aciklama']

@admin.register(Siparis)
class SiparisAdmin(admin.ModelAdmin):
    list_display = ['siparis_no', 'musteri', 'tarih', 'teslim_tarihi', 'durum', 'toplam_tutar_goster', 'dosya_var_mi']
    list_filter = ['durum', 'tarih', 'teslim_tarihi']
    search_fields = ['siparis_no', 'musteri__ad', 'musteri__kod']
    date_hierarchy = 'tarih'
    ordering = ['-tarih']
    
    # Form düzeni
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('siparis_no', 'musteri', 'durum')
        }),
        ('Tarihler', {
            'fields': ('tarih', 'teslim_tarihi')
        }),
        ('Ek Bilgiler', {
            'fields': ('notlar', 'dosya'),
            'classes': ('collapse',)  # Varsayılan olarak kapalı
        }),
    )
    
    # Inline olarak sipariş kalemlerini göster
    inlines = [SiparisKalemInline, SiparisDosyaInline]
    
    # Müşteri seçimi için otomatik tamamlama
    autocomplete_fields = ['musteri']
    
    # Custom actions
    actions = ['is_emirleri_olustur_action']
    
    # Toplam tutarı liste görünümünde göster
    def toplam_tutar_goster(self, obj):
        return f"{obj.toplam_tutar():,.2f} $"
    toplam_tutar_goster.short_description = 'Toplam Tutar'
    
    def dosya_var_mi(self, obj):
        if obj.dosya or obj.dosyalar.exists():
            return "✓"
        return "-"
    dosya_var_mi.short_description = 'Dosya'
    
    # Otomatik sipariş numarası üretimi için
    def get_changeform_initial_data(self, request):
        from datetime import datetime
        return {
            'siparis_no': f"SIP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
    
    def is_emirleri_olustur_action(self, request, queryset):
        """Seçilen siparişler için iş emirleri oluştur"""
        created_count = 0
        error_count = 0
        
        for siparis in queryset:
            try:
                # Her sipariş kalemi için iş emirleri oluştur
                for kalem in SiparisKalem.objects.filter(siparis=siparis):
                    # Bu ürün için iş akışı var mı?
                    is_akislari = IsAkisi.objects.filter(urun=kalem.urun, aktif=True)
                    
                    if not is_akislari.exists():
                        self.message_user(request, 
                            f"UYARI: {kalem.urun.ad} ürünü için aktif iş akışı bulunamadı!", 
                            level='warning')
                        continue
                    
                    # İlk aktif iş akışını kullan
                    is_akisi = is_akislari.first()
                    
                    # İş emirlerini oluştur (ana ürün + ara ürünler)
                    emirler = self._create_work_orders_recursive(
                        siparis, kalem, is_akisi, request.user
                    )
                    created_count += len(emirler)
                
                # Sipariş için tüm kalemler işlendikten sonra durumu güncelle
                siparis.durum = 'is_emirleri_olusturuldu'
                siparis.save(update_fields=['durum'])
                    
            except Exception as e:
                error_count += 1
                self.message_user(request, 
                    f"HATA: {siparis.siparis_no} için iş emirleri oluşturulamadı: {str(e)}", 
                    level='error')
        
        if created_count > 0:
            self.message_user(request, 
                f"{created_count} adet iş emri başarıyla oluşturuldu!", 
                level='success')
        
        if error_count > 0:
            self.message_user(request, 
                f"{error_count} sipariş için işlem başarısız!", 
                level='warning')
    
    is_emirleri_olustur_action.short_description = "Seçilen siparişler için iş emirleri oluştur"
    
    def _create_work_orders_for_order_item(self, siparis, kalem, is_akisi, user):
        """Sipariş kalemi için iş emirleri oluştur"""
        from datetime import datetime, timedelta
        
        # Ana iş emri numarası
        timestamp = datetime.now().strftime('%m%d%H%M%S')
        ana_emir_no = f"IE-{siparis.siparis_no}-{kalem.urun.kod}-{timestamp}"
        
        # İş akışındaki operasyonları al
        operasyonlar = is_akisi.operasyonlar.all().order_by('sira_no')
        
        if not operasyonlar.exists():
            raise ValueError(f"{is_akisi.ad} iş akışında operasyon bulunamadı!")
        
        # Varsayılan başlangıç tarihi (yarın)
        baslangic = datetime.now() + timedelta(days=1)
        baslangic = baslangic.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # BOM analizi - malzeme ve ara ürün gerekliliklerini hesapla
        bom_malzemeleri = self._get_bom_requirements(kalem.urun, kalem.miktar)
        ara_urunler = self._get_sub_product_requirements(kalem.urun, kalem.miktar)
        
        # Her operasyon için iş emri oluştur
        emirler = []
        for operasyon in operasyonlar:
            # Operasyon süresini hesapla
            planlanan_sure = float(operasyon.standart_sure or 0) + float(operasyon.hazirlik_suresi or 0)
            
            # Bitiş zamanını hesapla
            bitis = baslangic + timedelta(minutes=planlanan_sure)
            
            # İş emri oluştur
            is_emri = IsEmri.objects.create(
                emirNo=f"{ana_emir_no}-OP{operasyon.sira_no:02d}",
                ana_emirNo=ana_emir_no,
                siparis=siparis,
                siparis_kalemi=kalem,
                urun=kalem.urun,
                is_akisi=is_akisi,
                operasyon=operasyon,
                planlanan_miktar=kalem.miktar,
                planlanan_baslangic_tarihi=baslangic.date(),
                planlanan_baslangic_saati=baslangic.time(),
                planlanan_bitis_tarihi=bitis.date(),
                planlanan_bitis_saati=bitis.time(),
                planlanan_sure=planlanan_sure,
                gerekli_malzemeler=operasyon.operasyon_malzemeleri or [],
                gerekli_ara_urunler=operasyon.operasyon_ara_urunleri or [],
                olusturan=user
            )
            
            emirler.append(is_emri)
            
            # Sonraki operasyon için başlangıç zamanı
            baslangic = bitis
        
        # Operasyon bağımlılıklarını kur (sıralı)
        for i, is_emri in enumerate(emirler):
            if i > 0:
                is_emri.onceki_operasyonlar.add(emirler[i-1])
        
        return emirler
    
    def _create_work_orders_recursive(self, siparis, kalem, is_akisi, user):
        """Sipariş kalemi ve BOM ara ürünleri için recursive iş emirleri oluştur"""
        tum_emirler = []
        
        # Önce ara ürünler için iş emirleri oluştur
        ara_urun_emirleri = self._create_sub_product_work_orders(siparis, kalem, user)
        tum_emirler.extend(ara_urun_emirleri)
        
        # Sonra ana ürün için iş emirleri oluştur  
        ana_urun_emirleri = self._create_work_orders_for_order_item(siparis, kalem, is_akisi, user)
        tum_emirler.extend(ana_urun_emirleri)
        
        # Bağımlılıkları kur: Ana ürün emirleri ara ürün emirlerine bağımlı
        if ara_urun_emirleri and ana_urun_emirleri:
            # Ana ürünün ilk operasyonu (en düşük sıra numarası) bulunuyor
            ilk_ana_emir = min(ana_urun_emirleri, key=lambda x: x.operasyon.sira_no if x.operasyon else 999)
            
            # Ara ürün emirlerini ilk ana operasyona bağla
            for ara_emir in ara_urun_emirleri:
                ilk_ana_emir.onceki_operasyonlar.add(ara_emir)
        
        return tum_emirler
    
    def _create_sub_product_work_orders(self, siparis, kalem, user):
        """BOM'daki ara ürünler için iş emirleri oluştur"""
        ara_urun_emirleri = []
        
        # Ana ürünün BOM'undaki ara ürünleri bul
        if hasattr(kalem.urun, 'recete'):
            for recete in kalem.urun.recete.all():
                malzeme = recete.malzeme
                
                if malzeme.kategori == 'ara_urun':
                    # Bu ara ürün için iş akışı var mı?
                    ara_urun_akislari = IsAkisi.objects.filter(urun=malzeme, aktif=True)
                    
                    if ara_urun_akislari.exists():
                        ara_akisi = ara_urun_akislari.first()
                        
                        # Ara ürün için gereken miktar
                        gereken_miktar = recete.miktar * kalem.miktar
                        
                        # Ara ürün için iş emirleri oluştur (özel method)
                        ara_emirler = self._create_work_orders_for_sub_product(
                            siparis, malzeme, gereken_miktar, ara_akisi, user
                        )
                        ara_urun_emirleri.extend(ara_emirler)
        
        return ara_urun_emirleri
    
    def _create_work_orders_for_sub_product(self, siparis, ara_urun, miktar, is_akisi, user):
        """Ara ürün için iş emirleri oluştur"""
        from datetime import datetime, timedelta
        
        # Ana iş emri numarası (ara ürün için)
        timestamp = datetime.now().strftime('%m%d%H%M%S')
        ana_emir_no = f"IE-{siparis.siparis_no}-{ara_urun.kod}-{timestamp}"
        
        # İş akışındaki operasyonları al
        operasyonlar = is_akisi.operasyonlar.all().order_by('sira_no')
        
        if not operasyonlar.exists():
            raise ValueError(f"{is_akisi.ad} iş akışında operasyon bulunamadı!")
        
        # Varsayılan başlangıç tarihi (yarın)
        baslangic = datetime.now() + timedelta(days=1)
        baslangic = baslangic.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # BOM analizi - ara ürün için gerekli hammaddeler
        ara_urun_bom = self._get_bom_requirements(ara_urun, miktar)
        
        # Her operasyon için iş emri oluştur
        emirler = []
        for operasyon in operasyonlar:
            # Operasyon süresini hesapla
            planlanan_sure = float(operasyon.standart_sure or 0) + float(operasyon.hazirlik_suresi or 0)
            
            # Bitiş zamanını hesapla
            bitis = baslangic + timedelta(minutes=planlanan_sure)
            
            # İş emri oluştur (ara ürün için siparis_kalemi=None)
            is_emri = IsEmri.objects.create(
                emirNo=f"{ana_emir_no}-OP{operasyon.sira_no:02d}",
                ana_emirNo=ana_emir_no,
                siparis=siparis,
                siparis_kalemi=None,  # Ara ürün için None
                urun=ara_urun,
                is_akisi=is_akisi,
                operasyon=operasyon,
                planlanan_miktar=miktar,
                planlanan_baslangic_tarihi=baslangic.date(),
                planlanan_baslangic_saati=baslangic.time(),
                planlanan_bitis_tarihi=bitis.date(),
                planlanan_bitis_saati=bitis.time(),
                planlanan_sure=planlanan_sure,
                gerekli_malzemeler=operasyon.operasyon_malzemeleri or [],
                gerekli_ara_urunler=operasyon.operasyon_ara_urunleri or [],
                olusturan=user
            )
            
            emirler.append(is_emri)
            
            # Sonraki operasyon için başlangıç zamanı
            baslangic = bitis
        
        # Operasyon bağımlılıklarını kur (sıralı)
        for i, is_emri in enumerate(emirler):
            if i > 0:
                is_emri.onceki_operasyonlar.add(emirler[i-1])
        
        return emirler
    
    def _group_orders_by_product(self, emirler):
        """İş emirlerini ürüne göre grupla"""
        from itertools import groupby
        
        # Ürüne göre sırala ve grupla
        sorted_emirler = sorted(emirler, key=lambda x: x.urun.id)
        grouped = []
        
        for urun_id, group in groupby(sorted_emirler, key=lambda x: x.urun.id):
            grouped.append(list(group))
            
        return grouped
    
    def _get_bom_requirements(self, urun, miktar):
        """BOM gerekliliklerini getir (sadece hammaddeler)"""
        requirements = []
        if hasattr(urun, 'recete'):
            for recete in urun.recete.all():
                if recete.malzeme.kategori == 'hammadde':
                    requirements.append({
                        'malzeme': recete.malzeme.ad,
                        'miktar': float(recete.miktar * miktar),
                        'birim': recete.malzeme.birim,
                        'kategori': recete.malzeme.kategori
                    })
        return requirements
    
    def _get_sub_product_requirements(self, urun, miktar):
        """Ara ürün gerekliliklerini getir"""
        requirements = []
        if hasattr(urun, 'recete'):
            for recete in urun.recete.all():
                if recete.malzeme.kategori == 'ara_urun':
                    requirements.append({
                        'ara_urun': recete.malzeme.ad,
                        'miktar': float(recete.miktar * miktar),
                        'birim': recete.malzeme.birim
                    })
        return requirements
        
# Proxy Model for Planlama
class MalzemePlanlama(Siparis):
    class Meta:
        proxy = True
        verbose_name = "Malzeme Planlama"
        verbose_name_plural = "Malzeme Planlama"
        
@admin.register(MalzemePlanlama)
class MalzemePlanlamaAdmin(admin.ModelAdmin):
    change_list_template = 'admin/malzeme_planlama_list.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        # Debug: Tedarikçiler listesi (Unicode hatası için devre dışı)
        # print("Tedarikci listesi:", list(Tedarikci.objects.filter(aktif=True).values('id', 'kod', 'ad')))
        if request.method == 'POST' and request.POST.get('action') == 'malzeme_planla':
            selected_ids = request.POST.getlist('selected_siparisler')
            if selected_ids:
                # Seçilen siparişleri session'a kaydet
                request.session['selected_siparis_ids'] = selected_ids
                return redirect('admin:production_malzemeplanlama_malzeme_listesi')
        
        # Beklemedeki siparişleri al
        bekleyen_siparisler = Siparis.objects.filter(durum='beklemede').select_related('musteri')
        
        extra_context = extra_context or {}
        extra_context['bekleyen_siparisler'] = bekleyen_siparisler
        extra_context['title'] = 'Malzeme Planlama - Bekleyen Siparişler'
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('malzeme-listesi/', self.admin_site.admin_view(self.malzeme_listesi_view), name='production_malzemeplanlama_malzeme_listesi'),
        ]
        return custom_urls + urls

    def malzeme_listesi_view(self, request):
        selected_ids = request.session.get('selected_siparis_ids', [])
        if not selected_ids:
            messages.error(request, "Lütfen önce sipariş seçin.")
            return redirect('admin:production_malzemeplanlama_changelist')
        
        # POST işlemi - form submit edildiğinde
        if request.method == 'POST':
            from .models import MalzemeIhtiyac  # Import'u buraya ekleyin
            
            siparisler = Siparis.objects.filter(id__in=selected_ids)
            malzeme_listesi = self.calculate_materials(siparisler)
            
            # Her malzeme için ihtiyaç kaydı oluştur
            created_count = 0
            for malzeme in malzeme_listesi:
                islem_key = f"islem_{malzeme['ad']}"
                islem_tipi = request.POST.get(islem_key)
                
                if islem_tipi:
                    MalzemeIhtiyac.objects.create(
                        malzeme_adi=malzeme['ad'],
                        miktar=malzeme['miktar'],
                        birim=malzeme['birim'],
                        islem_tipi=islem_tipi,
                        ilgili_siparisler=malzeme['siparisler'],
                        ilgili_urunler=malzeme['urunler'],
                        olusturan=request.user
                    )
                    created_count += 1
            # İlgili siparişlerin durumunu güncelle
            siparis_ids = set()
            for malzeme in malzeme_listesi:
                for siparis_no in malzeme['siparisler']:
                    siparis = Siparis.objects.filter(siparis_no=siparis_no).first()
                    if siparis:
                        siparis_ids.add(siparis.id)
        
                    # Siparişlerin durumunu güncelle
                    if siparis_ids:
                        Siparis.objects.filter(id__in=siparis_ids).update(durum='malzeme_planlandi')
                        
            messages.success(request, f"{created_count} adet malzeme ihtiyacı kaydedildi.")
            return redirect('admin:production_malzemeplanlama_changelist')
        
        # GET işlemi - normal görüntüleme
        siparisler = Siparis.objects.filter(id__in=selected_ids).prefetch_related('kalemler__urun')
        malzeme_listesi = self.calculate_materials(siparisler)
        
        context = {
            'title': 'Malzeme İhtiyaç Listesi',
            'malzeme_listesi': malzeme_listesi,
            'siparisler': siparisler,
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        
        return render(request, 'admin/malzeme_listesi.html', context)
    
    def calculate_materials(self, siparisler):
        """BOM'ları derinlemesine analiz ederek hammadde listesi oluştur"""
        malzemeler = defaultdict(lambda: {'miktar': 0, 'birim': '', 'siparisler': [], 'urunler': set()})
    
        def get_hammaddeler(urun, miktar, siparis_no, ana_urun, ara_urun_yolu=[]):
            """Recursive olarak hammaddeleri bul"""
            if urun.kategori == 'hammadde':
                # Hammadde ise direkt ekle
                malzemeler[urun.ad]['miktar'] += miktar
                malzemeler[urun.ad]['birim'] = urun.birim
                malzemeler[urun.ad]['siparisler'].append(siparis_no)
                
                # Ürün bilgisini oluştur
                if ara_urun_yolu:
                    # Eğer ara ürün varsa, ana ürün ve ara ürünü göster
                    urun_bilgisi = f"{ana_urun} (Ara Ürün: {' > '.join(ara_urun_yolu)})"
                else:
                    # Direkt ana üründe kullanılıyorsa
                    urun_bilgisi = ana_urun
                
                malzemeler[urun.ad]['urunler'].add(urun_bilgisi)
            else:
                # Ara ürün veya bitmiş ürün ise reçetesini aç
                yeni_ara_urun_yolu = ara_urun_yolu + [urun.ad] if urun.ad != ana_urun else ara_urun_yolu
                
                for recete_item in urun.recete.all():
                    gerekli_miktar = recete_item.miktar * miktar
                    get_hammaddeler(recete_item.malzeme, gerekli_miktar, siparis_no, ana_urun, yeni_ara_urun_yolu)
        
        # Her sipariş kalemini işle
        for siparis in siparisler:
            for kalem in siparis.kalemler.all():
                get_hammaddeler(kalem.urun, kalem.miktar, siparis.siparis_no, kalem.urun.ad, [])
        
        # Sonuçları düzenle
        malzeme_listesi = []
        for malzeme_ad, detay in malzemeler.items():
            malzeme_listesi.append({
                'ad': malzeme_ad,
                'miktar': detay['miktar'],
                'birim': detay['birim'],
                'siparisler': list(set(detay['siparisler'])),
                'urunler': list(detay['urunler'])
            })
        
        return sorted(malzeme_listesi, key=lambda x: x['ad'])
    
@admin.register(MalzemeIhtiyac)
class MalzemeIhtiyacAdmin(admin.ModelAdmin):
    list_display = ['malzeme_adi', 'miktar', 'birim', 'islem_tipi', 'durum', 'olusturulma_tarihi', 'satin_alma_butonu']
    list_filter = ['islem_tipi', 'durum', 'olusturulma_tarihi']
    search_fields = ['malzeme_adi']
    readonly_fields = ['olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi']
    
    change_list_template = 'admin/malzeme_ihtiyac_list.html'
    
    fieldsets = (
        ('Malzeme Bilgileri', {
            'fields': ('malzeme_adi', 'miktar', 'birim')
        }),
        ('İşlem Bilgileri', {
            'fields': ('islem_tipi', 'durum', 'notlar')
        }),
        ('İlişkili Bilgiler', {
            'fields': ('ilgili_siparisler', 'ilgili_urunler')
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST' and request.POST.get('action') == 'satin_alma_olustur':
            import json
            from datetime import datetime
            
            try:
                siparis_data = json.loads(request.POST.get('siparis_data'))
                
                # Sipariş no oluştur
                siparis_no = f"SA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                # Satın alma siparişi oluştur
                siparis = SatinAlmaSiparisi.objects.create(
                    siparis_no=siparis_no,
                    tedarikci_id=siparis_data['tedarikci'],
                    tarih=timezone.now().date(),
                    teslim_tarihi=timezone.now().date(),  # Geçici
                    toplam_tutar=0,  # Geçici
                    olusturan=request.user
                )
                
                toplam = 0
                for malzeme_data in siparis_data['malzemeler']:
                    # İlgili malzeme ihtiyacını bul
                    malzeme_ihtiyac = MalzemeIhtiyac.objects.get(id=malzeme_data['malzeme_ihtiyac_id'])
                    
                    # Satın alma kalemi oluştur
                    kalem = SatinAlmaKalemi.objects.create(
                        siparis=siparis,
                        malzeme_ihtiyaci=malzeme_ihtiyac,
                        miktar=malzeme_data['miktar'],
                        birim_fiyat=malzeme_data['birim_fiyat']
                    )
                    
                    # Malzeme ihtiyacının durumunu güncelle
                    malzeme_ihtiyac.durum = 'siparis_verildi'
                    malzeme_ihtiyac.save()
                    
                    toplam += kalem.toplam_fiyat
                
                # Toplam tutarı güncelle
                siparis.toplam_tutar = toplam
                siparis.save()
                
                messages.success(request, f"Satın alma siparişi {siparis_no} başarıyla oluşturuldu.")
                
            except Exception as e:
                messages.error(request, f"Hata oluştu: {str(e)}")
        
        # Tedarikçi listesini context'e ekle
        extra_context = extra_context or {}
        extra_context['tedarikciler'] = Tedarikci.objects.filter(aktif=True).values('id', 'kod', 'ad')
        
        return super().changelist_view(request, extra_context=extra_context)
        
    def satin_alma_butonu(self, obj):
        if obj.islem_tipi == 'satin_al' and obj.durum == 'beklemede':
            return format_html('<input type="checkbox" class="satin-alma-checkbox" data-id="{}" data-malzeme="{}" data-miktar="{}" data-birim="{}">', 
                             obj.id, obj.malzeme_adi, obj.miktar, obj.birim)
        return "-"
    satin_alma_butonu.short_description = "Seç"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.olusturan = request.user
        super().save_model(request, obj, form, change)
        
@admin.register(Tedarikci)
class TedarikciAdmin(admin.ModelAdmin):
    list_display = ['kod', 'ad', 'telefon', 'email', 'aktif']
    list_filter = ['aktif']
    search_fields = ['ad', 'kod', 'email']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('kod', 'ad', 'aktif')
        }),
        ('İletişim Bilgileri', {
            'fields': ('telefon', 'email', 'adres')
        }),
        ('Vergi Bilgileri', {
            'fields': ('vergi_no', 'vergi_dairesi'),
            'classes': ('collapse',)
        }),
    )
    
class SatinAlmaKalemiInline(admin.TabularInline):
    model = SatinAlmaKalemi
    extra = 0
    readonly_fields = [
        'malzeme_ihtiyaci', 'miktar', 'birim_fiyat', 'toplam_fiyat',
        'gelen_toplam_miktar', 'kalan_miktar', 'tamamlanma_yuzdesi_goster', 'gelis_durumu_renkli'
    ]
    fields = [
        'malzeme_ihtiyaci', 'miktar', 'birim_fiyat', 'toplam_fiyat',
        'gelen_toplam_miktar', 'kalan_miktar', 'tamamlanma_yuzdesi_goster', 'gelis_durumu_renkli'
    ]
    
    def gelen_toplam_miktar(self, obj):
        """Gelen toplam miktar"""
        return f"{obj.gelen_toplam_miktar} {obj.malzeme_ihtiyaci.birim}"
    gelen_toplam_miktar.short_description = 'Gelen Toplam'
    
    def kalan_miktar(self, obj):
        """Kalan miktar"""
        return f"{obj.kalan_miktar} {obj.malzeme_ihtiyaci.birim}"
    kalan_miktar.short_description = 'Kalan'
    
    def tamamlanma_yuzdesi_goster(self, obj):
        """Tamamlanma yüzdesi göster"""
        yuzde = obj.tamamlanma_yuzdesi
        return f"%{yuzde:.1f}"
    tamamlanma_yuzdesi_goster.short_description = 'Tamamlanma'
    
    def gelis_durumu_renkli(self, obj):
        """Renk kodlu durum"""
        durum = obj.gelis_durumu
        renkler = {
            'bekliyor': '#dc3545',  # Kırmızı
            'kismi': '#ffc107',     # Sarı  
            'tam': '#28a745',       # Yeşil
            'fazla': '#17a2b8'      # Mavi
        }
        durum_metni = {
            'bekliyor': '⏳ Bekliyor',
            'kismi': '🟡 Kısmi',
            'tam': '✅ Tam',
            'fazla': '⚠️ Fazla'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            renkler.get(durum, '#6c757d'),
            durum_metni.get(durum, durum.title())
        )
    gelis_durumu_renkli.short_description = 'Durum'

class SatinAlmaTeslimGuncellemeInline(admin.TabularInline):
    model = SatinAlmaTeslimGuncelleme
    extra = 0
    readonly_fields = ['eski_teslim_tarihi', 'guncelleyen', 'guncelleme_tarihi']
    fields = ['eski_teslim_tarihi', 'yeni_teslim_tarihi', 'aciklama', 'guncelleyen', 'guncelleme_tarihi']
    can_delete = False

@admin.register(SatinAlmaSiparisi)
class SatinAlmaSiparisiAdmin(admin.ModelAdmin):
    list_display = [
        'siparis_no', 'tedarikci', 'tarih', 'teslim_tarihi', 'guncel_teslim_tarihi', 
        'toplam_tutar', 'durum', 'kalem_durum_ozeti_goster', 'genel_tamamlanma_goster', 'siparis_durumu_renkli_goster', 'olusturan'
    ]
    list_editable = ['guncel_teslim_tarihi']
    change_form_template = 'admin/change_form_satinalma.html'
    list_filter = ['tarih', 'tedarikci', 'durum']
    search_fields = ['siparis_no', 'tedarikci__ad']
    readonly_fields = ['siparis_no', 'durum', 'olusturan', 'olusturulma_tarihi']
    inlines = [SatinAlmaKalemiInline, SatinAlmaTeslimGuncellemeInline]
    
    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('siparis_no', 'tedarikci', 'tarih', 'teslim_tarihi', 'guncel_teslim_tarihi', 'toplam_tutar', 'durum')
        }),
        ('Dosya', {
            'fields': ('siparis_dosyasi',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturan', 'olusturulma_tarihi'),
            'classes': ('collapse',)
        }),
    )
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/export/', self.admin_site.admin_view(self.export_pdf_view), name='production_satinalmasiparisi_export'),
        ]
        return custom_urls + urls

    def export_pdf_view(self, request, object_id):
        siparis = get_object_or_404(SatinAlmaSiparisi, pk=object_id)
        
        context = {
            'siparis': siparis,
            'kalemler': siparis.kalemler.all(),
            'today': timezone.now().date(),
        }
    
        return render(request, 'admin/satinalma_siparisi_print.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_url'] = reverse('admin:production_satinalmasiparisi_export', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def guncel_teslim_goster(self, obj):
        if obj.guncel_teslim_tarihi:
            if obj.guncel_teslim_tarihi != obj.teslim_tarihi:
                return format_html('<span style="color: red; font-weight: bold;">{}</span>', 
                                obj.guncel_teslim_tarihi.strftime('%d.%m.%Y'))
            return obj.guncel_teslim_tarihi.strftime('%d.%m.%Y')
        return obj.teslim_tarihi.strftime('%d.%m.%Y')
    guncel_teslim_goster.short_description = 'Güncel Teslim'
    
    def save_model(self, request, obj, form, change):
        if change:  # Mevcut kayıt güncelleniyor
            # Eski kaydı al
            old_obj = SatinAlmaSiparisi.objects.get(pk=obj.pk)
            
            # Güncel teslim tarihi değişmişse kaydet
            if 'guncel_teslim_tarihi' in form.changed_data:
                if obj.guncel_teslim_tarihi:
                    SatinAlmaTeslimGuncelleme.objects.create(
                        siparis=obj,
                        eski_teslim_tarihi=old_obj.guncel_teslim_tarihi or old_obj.teslim_tarihi,
                        yeni_teslim_tarihi=obj.guncel_teslim_tarihi,
                        guncelleyen=request.user,
                        aciklama=f"Teslim tarihi güncellendi"
                    )
        else:  # Yeni kayıt
            # İlk oluşturmada güncel teslim tarihini normal teslim tarihiyle aynı yap
            if not obj.guncel_teslim_tarihi:
                obj.guncel_teslim_tarihi = obj.teslim_tarihi
        
        super().save_model(request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
    
        # Liste görünümünden güncelleme kontrolü
        if hasattr(self, '_list_editable_updates'):
            for obj_id, new_date in self._list_editable_updates.items():
                obj = SatinAlmaSiparisi.objects.get(pk=obj_id)
                old_date = obj.guncel_teslim_tarihi or obj.teslim_tarihi
                
                if new_date and new_date != old_date:
                    SatinAlmaTeslimGuncelleme.objects.create(
                        siparis=obj,
                        eski_teslim_tarihi=old_date,
                        yeni_teslim_tarihi=new_date,
                        guncelleyen=request.user,
                        aciklama="Liste görünümünden güncellendi"
                    )

    def changelist_view(self, request, extra_context=None):
        # POST isteğinde ve kaydet butonuna basıldıysa
        if request.method == 'POST' and '_save' in request.POST:
            # Güncel teslim tarihi değişikliklerini yakala
            self._list_editable_updates = {}
            
            for key, value in request.POST.items():
                if key.startswith('form-') and key.endswith('-guncel_teslim_tarihi'):
                    # form-0-guncel_teslim_tarihi gibi bir key'den ID'yi çıkar
                    form_index = key.split('-')[1]
                    obj_id_key = f'form-{form_index}-id'
                    
                    if obj_id_key in request.POST:
                        obj_id = request.POST[obj_id_key]
                        if value:  # Eğer tarih değeri varsa
                            from datetime import datetime
                            try:
                                new_date = datetime.strptime(value, '%Y-%m-%d').date()
                                old_obj = SatinAlmaSiparisi.objects.get(pk=obj_id)
                                
                                if new_date != (old_obj.guncel_teslim_tarihi or old_obj.teslim_tarihi):
                                    self._list_editable_updates[obj_id] = new_date
                            except:
                                pass
        
        response = super().changelist_view(request, extra_context=extra_context)
        
        # Güncellemeleri kaydet
        if hasattr(self, '_list_editable_updates') and self._list_editable_updates:
            for obj_id, new_date in self._list_editable_updates.items():
                obj = SatinAlmaSiparisi.objects.get(pk=obj_id)
                old_date = obj.guncel_teslim_tarihi or obj.teslim_tarihi
                
                SatinAlmaTeslimGuncelleme.objects.create(
                    siparis=obj,
                    eski_teslim_tarihi=old_date,
                    yeni_teslim_tarihi=new_date,
                    guncelleyen=request.user,
                    aciklama="Liste görünümünden güncellendi"
                )
        
        return response
    
    def kalem_durum_ozeti_goster(self, obj):
        """Kalem durumlarının özeti"""
        toplam = obj.toplam_kalem_sayisi
        tamamlanan = obj.tamamlanan_kalem_sayisi
        kismi = obj.kismi_kalem_sayisi
        bekleyen = obj.bekleyen_kalem_sayisi
        
        return format_html(
            '<small>T:{} / ✅:{} / 🟡:{} / ⏳:{}</small>',
            toplam, tamamlanan, kismi, bekleyen
        )
    kalem_durum_ozeti_goster.short_description = 'Kalem Durumu'
    
    def genel_tamamlanma_goster(self, obj):
        """Genel tamamlanma yüzdesini göster"""
        yuzde = obj.genel_tamamlanma_yuzdesi
        if yuzde >= 100:
            renk = '#28a745'  # Yeşil
        elif yuzde >= 50:
            renk = '#ffc107'  # Sarı  
        elif yuzde > 0:
            renk = '#fd7e14'  # Turuncu
        else:
            renk = '#dc3545'  # Kırmızı
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">%{}</span>',
            renk, f'{yuzde:.1f}'
        )
    genel_tamamlanma_goster.short_description = 'Tamamlanma'
    
    def siparis_durumu_renkli_goster(self, obj):
        """Renk kodlu sipariş durumu"""
        durum = obj.siparis_durumu
        renkler = {
            'bekliyor': '#dc3545',    # Kırmızı
            'kismi': '#ffc107',       # Sarı
            'tamamlandi': '#28a745',  # Yeşil
            'bos': '#6c757d'          # Gri
        }
        durum_metni = {
            'bekliyor': '⏳ Bekliyor',
            'kismi': '🟡 Kısmi',
            'tamamlandi': '✅ Tamamlandı',
            'bos': '📋 Boş'
        }
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            renkler.get(durum, '#6c757d'),
            durum_metni.get(durum, durum.title())
        )
    siparis_durumu_renkli_goster.short_description = 'Sipariş Durumu'

from django import forms

class MalzemeGelisAdminForm(forms.ModelForm):
    class Meta:
        model = MalzemeGelis
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eğer instance varsa (düzenleme modunda) ve satinalma_kalemi varsa birim bilgisini label'a ekle
        if (self.instance and self.instance.pk and 
            hasattr(self.instance, 'satinalma_kalemi') and 
            self.instance.satinalma_kalemi):
            try:
                birim = self.instance.malzeme_birim
                self.fields['gelen_miktar'].label = f"Gelen Miktar ({birim})"
                self.fields['gelen_miktar'].help_text = f"Birim: {birim}"
            except Exception:
                # Birim bilgisi alınamazsa varsayılan label'ı kullan
                pass

@admin.register(MalzemeGelis)
class MalzemeGelisAdmin(admin.ModelAdmin):
    form = MalzemeGelisAdminForm
    list_display = [
        'satis_siparisi', 'satinalma_siparisi', 'malzeme_adi', 'gelen_miktar_birim', 
        'birim_fiyat', 'para_birimi', 'toplam_tutar',
        'gelis_tarihi', 'irsaliye_no', 'kaydeden'
    ]
    list_filter = ['gelis_tarihi', 'kayit_tarihi']
    search_fields = [
        'satinalma_siparisi__siparis_no', 
        'satinalma_kalemi__malzeme_ihtiyaci__malzeme_adi',
        'irsaliye_no', 'fatura_no'
    ]
    readonly_fields = ['kayit_tarihi', 'kaydeden']
    date_hierarchy = 'gelis_tarihi'
    ordering = ['-gelis_tarihi', '-kayit_tarihi']
    # change_list_template = 'admin/malzeme_gelis_changelist.html'  # Geçici olarak devre dışı
    
    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('satis_siparisi', 'satinalma_siparisi', 'satinalma_kalemi')
        }),
        ('Geliş Bilgileri', {
            'fields': ('gelen_miktar', 'gelis_tarihi'),
            'description': 'Gelen miktar için birim otomatik olarak seçilen malzeme kaleminden alınır.'
        }),
        ('Fiyat Bilgileri', {
            'fields': ('birim_fiyat', 'para_birimi', 'toplam_tutar')
        }),
        ('Evrak Bilgileri', {
            'fields': ('irsaliye_no', 'fatura_no', 'evrak_dosyasi')
        }),
        ('Ek Bilgiler', {
            'fields': ('notlar',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('kaydeden', 'kayit_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def malzeme_adi(self, obj):
        """Malzeme adını göster"""
        try:
            if obj.satinalma_kalemi and obj.satinalma_kalemi.malzeme_ihtiyaci:
                return obj.satinalma_kalemi.malzeme_ihtiyaci.malzeme_adi
        except Exception:
            pass
        return "-"
    malzeme_adi.short_description = 'Malzeme Adı'
    
    def gelen_miktar_birim(self, obj):
        """Gelen miktar ve birimini göster"""
        try:
            birim = obj.malzeme_birim
            return f"{obj.gelen_miktar} {birim}" if birim else str(obj.gelen_miktar)
        except Exception:
            return str(obj.gelen_miktar)
    gelen_miktar_birim.short_description = 'Gelen Miktar'
    
    def save_model(self, request, obj, form, change):
        """Kaydetme sırasında kullanıcıyı otomatik ata"""
        if not change:  # Yeni kayıtsa
            obj.kaydeden = request.user
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """İlişkili alanlar için filtreler"""
        # Şimdilik filtrelemeyi devre dışı bırakalım - validation hatasına sebep oluyor
        # TODO: Daha sonra dinamik filtreleme eklenecek
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def changelist_view(self, request, extra_context=None):
        """Changelist view'da rapor verilerini ekle"""
        extra_context = extra_context or {}
        
        # Excel export kontrolü
        if request.GET.get('_export') == 'excel':
            return self.export_excel(request)
        
        try:
            # Son 30 günün istatistikleri
            from datetime import datetime, timedelta
            today = timezone.now().date()
            son_30_gun = today - timedelta(days=30)
            
            # Temel istatistikler
            toplam_gelis = MalzemeGelis.objects.count()
            son_30_gun_gelis = MalzemeGelis.objects.filter(gelis_tarihi__gte=son_30_gun).count()
            
            # Para birimi bazında toplam tutarlar (sadece veri varsa)
            from django.db.models import Sum, Count
            para_birimi_toplamlar = []
            tedarikci_istatistikleri = []
            
            if toplam_gelis > 0:
                para_birimi_toplamlar = MalzemeGelis.objects.values('para_birimi').annotate(
                    toplam=Sum('toplam_tutar')
                ).order_by('-toplam')
                
                # Tedarikçi bazında istatistikler
                tedarikci_istatistikleri = MalzemeGelis.objects.values(
                    'satinalma_siparisi__tedarikci__ad'
                ).annotate(
                    gelis_sayisi=Count('id'),
                    toplam_tutar=Sum('toplam_tutar')
                ).order_by('-gelis_sayisi')[:10]
            
            extra_context.update({
                'toplam_gelis': toplam_gelis,
                'son_30_gun_gelis': son_30_gun_gelis,
                'para_birimi_toplamlar': para_birimi_toplamlar,
                'tedarikci_istatistikleri': tedarikci_istatistikleri
            })
        except Exception as e:
            # Hata durumunda boş değerler
            extra_context.update({
                'toplam_gelis': 0,
                'son_30_gun_gelis': 0,
                'para_birimi_toplamlar': [],
                'tedarikci_istatistikleri': []
            })
        
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        """Custom URL'ler ekle"""
        urls = super().get_urls()
        from django.urls import path
        custom_urls = [
            path('tedarikci-performans/', self.admin_site.admin_view(self.tedarikci_performans_view), name='malzeme_gelis_tedarikci_performans'),
        ]
        return custom_urls + urls
    
    def tedarikci_performans_view(self, request):
        """Tedarikçi performans raporu"""
        from django.shortcuts import render
        from django.db.models import Sum, Count, Avg, Q
        from datetime import datetime, timedelta
        
        # Tarih filtresi
        baslangic_tarihi = request.GET.get('baslangic', None)
        bitis_tarihi = request.GET.get('bitis', None)
        
        if not baslangic_tarihi:
            baslangic_tarihi = (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not bitis_tarihi:
            bitis_tarihi = timezone.now().date().strftime('%Y-%m-%d')
        
        # Tedarikçi performans verileri
        tedarikci_performans = MalzemeGelis.objects.filter(
            gelis_tarihi__range=[baslangic_tarihi, bitis_tarihi]
        ).values(
            'satinalma_siparisi__tedarikci__ad',
            'satinalma_siparisi__tedarikci__kod'
        ).annotate(
            toplam_gelis=Count('id'),
            toplam_tutar=Sum('toplam_tutar'),
            ortalama_tutar=Avg('toplam_tutar'),
            benzersiz_siparis=Count('satinalma_siparisi', distinct=True),
            benzersiz_malzeme=Count('satinalma_kalemi__malzeme_ihtiyaci__malzeme_adi', distinct=True)
        ).order_by('-toplam_tutar')
        
        # Zamanında teslimat analizi
        zamaninda_teslimat = []
        for tp in tedarikci_performans:
            tedarikci_ad = tp['satinalma_siparisi__tedarikci__ad']
            
            # Bu tedarikçinin siparişleri
            siparisler = SatinAlmaSiparisi.objects.filter(
                tedarikci__ad=tedarikci_ad,
                gelisler__gelis_tarihi__range=[baslangic_tarihi, bitis_tarihi]
            ).distinct()
            
            zamaninda = 0
            toplam_siparis = siparisler.count()
            
            for siparis in siparisler:
                teslim_tarihi = siparis.guncel_teslim_tarihi or siparis.teslim_tarihi
                if siparis.gelisler.filter(gelis_tarihi__lte=teslim_tarihi).exists():
                    zamaninda += 1
            
            zamaninda_yuzde = (zamaninda / toplam_siparis * 100) if toplam_siparis > 0 else 0
            
            tp['zamaninda_teslimat'] = zamaninda_yuzde
            tp['zamaninda_siparis'] = zamaninda
            tp['toplam_siparis_sayisi'] = toplam_siparis
        
        context = {
            'title': 'Tedarikçi Performans Raporu',
            'tedarikci_performans': tedarikci_performans,
            'baslangic_tarihi': baslangic_tarihi,
            'bitis_tarihi': bitis_tarihi,
            'opts': MalzemeGelis._meta,
            'has_view_permission': True,
        }
        
        return render(request, 'admin/tedarikci_performans.html', context)
    
    def export_excel(self, request):
        """Excel export işlemi"""
        from django.http import HttpResponse
        import csv
        from io import StringIO
        
        # Filtreleri uygula
        queryset = self.get_queryset(request)
        
        # CSV response oluştur
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="malzeme_gelisleri_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # BOM ekle (Excel için UTF-8 desteği)
        response.write('\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        
        # Başlık satırı
        writer.writerow([
            'Satış Siparişi',
            'Satın Alma Siparişi', 
            'Malzeme Adı',
            'Gelen Miktar',
            'Birim',
            'Birim Fiyat',
            'Para Birimi', 
            'Toplam Tutar',
            'Geliş Tarihi',
            'İrsaliye No',
            'Fatura No',
            'Kaydeden',
            'Kayıt Tarihi'
        ])
        
        # Veri satırları
        for obj in queryset:
            try:
                writer.writerow([
                    obj.satis_siparisi.siparis_no if obj.satis_siparisi else '',
                    obj.satinalma_siparisi.siparis_no,
                    obj.satinalma_kalemi.malzeme_ihtiyaci.malzeme_adi if obj.satinalma_kalemi and obj.satinalma_kalemi.malzeme_ihtiyaci else '',
                    obj.gelen_miktar,
                    obj.malzeme_birim,
                    obj.birim_fiyat,
                    obj.para_birimi,
                    obj.toplam_tutar,
                    obj.gelis_tarihi.strftime('%d.%m.%Y'),
                    obj.irsaliye_no,
                    obj.fatura_no or '',
                    obj.kaydeden.username if obj.kaydeden else '',
                    obj.kayit_tarihi.strftime('%d.%m.%Y %H:%M')
                ])
            except Exception as e:
                # Hata durumunda boş satır ekle
                writer.writerow(['HATA'] * 13)
        
        return response


# =============================================================================
# ÜRETİM MODÜLÜ ADMIN
# =============================================================================

@admin.register(StandardIsAdimi)
class StandardIsAdimiAdmin(admin.ModelAdmin):
    list_display = [
        'kod', 'ad', 'kategori_renkli', 'tahmini_sure_birim', 
        'gerekli_istasyon_tipi', 'aktif'
    ]
    list_filter = ['kategori', 'gerekli_istasyon_tipi', 'aktif']
    search_fields = ['kod', 'ad', 'aciklama']
    list_editable = ['aktif']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('kod', 'ad', 'kategori', 'aciklama')
        }),
        ('Teknik Bilgiler', {
            'fields': ('tahmini_sure_birim', 'gerekli_istasyon_tipi')
        }),
        ('Görsel Tasarım', {
            'fields': ('renk', 'ikon', 'aktif'),
            'classes': ('collapse',)
        }),
    )
    
    def kategori_renkli(self, obj):
        """Kategori renk kodlu göster"""
        kategori_renkler = {
            'kesim': '#dc3545',
            'isleme': '#007bff', 
            'montaj': '#28a745',
            'kalite': '#ffc107',
            'paketleme': '#6610f2',
            'boya': '#e83e8c',
            'kaynak': '#fd7e14',
            'tornalama': '#20c997',
            'frezeleme': '#17a2b8',
            'zimpara': '#6c757d',
        }
        renk = kategori_renkler.get(obj.kategori, '#007bff')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            renk, obj.get_kategori_display()
        )
    kategori_renkli.short_description = 'Kategori'

@admin.register(IsIstasyonu)
class IsIstasyonuAdmin(admin.ModelAdmin):
    list_display = [
        'kod', 'ad', 'tip', 'durum_renkli', 'lokasyon', 
        'gunluk_calisma_saati', 'saatlik_maliyet', 'doluluk_goster', 'aktif'
    ]
    list_filter = ['tip', 'durum', 'aktif', 'olusturulma_tarihi']
    search_fields = ['kod', 'ad', 'lokasyon']
    list_editable = ['aktif']
    readonly_fields = ['olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('kod', 'ad', 'tip', 'durum', 'lokasyon', 'aciklama')
        }),
        ('Kapasite ve Performans', {
            'fields': ('gunluk_calisma_saati', 'gerekli_operator_sayisi')
        }),
        ('Maliyet Bilgileri', {
            'fields': ('saatlik_maliyet',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('aktif', 'olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def durum_renkli(self, obj):
        """Renk kodlu durum gösterimi"""
        durum_emoji = {
            'aktif': '✅',
            'bakim': '🔧',
            'arizali': '🚫',
            'pasif': '⏸️'
        }
        emoji = durum_emoji.get(obj.durum, '❓')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            obj.durum_renk,
            emoji,
            obj.get_durum_display()
        )
    durum_renkli.short_description = 'Durum'
    
    
    def doluluk_goster(self, obj):
        """Doluluk oranı gösterimi"""
        oran = obj.doluluk_orani
        if oran >= 90:
            renk = '#dc3545'  # Kırmızı - Dolu
        elif oran >= 70:
            renk = '#ffc107'  # Sarı - Orta
        elif oran >= 30:
            renk = '#28a745'  # Yeşil - Düşük
        else:
            renk = '#17a2b8'  # Mavi - Boş
        
        return format_html(
            '<div style="width: 60px; background: #f0f0f0; border-radius: 10px; padding: 2px;">'
            '<div style="width: {}%; background: {}; height: 16px; border-radius: 8px; text-align: center; color: white; font-size: 10px; line-height: 16px;">'
            '{}%</div></div>',
            oran, renk, int(oran)
        )
    doluluk_goster.short_description = 'Doluluk'
    
    def save_model(self, request, obj, form, change):
        """Kaydet sırasında kullanıcıyı ata"""
        if not change:  # Yeni kayıt
            obj.olusturan = request.user
        super().save_model(request, obj, form, change)


class IsAkisiOperasyonInline(admin.TabularInline):
    """İş akışı operasyonları inline"""
    model = IsAkisiOperasyon
    extra = 1
    fields = [
        'sira_no_goster', 'operasyon_adi', 'istasyon', 'standart_sure', 
        'hazirlik_suresi', 'kalite_kontrolu_gerekli', 'kritik'
    ]
    readonly_fields = ['sira_no_goster']
    
    def sira_no_goster(self, obj):
        """Sıra numarasını göster"""
        if obj.pk and obj.sira_no:
            return f"{obj.sira_no:02d}"
        return "Otomatik"
    sira_no_goster.short_description = 'Sıra No'
    
    ordering = ['sira_no']


@admin.register(IsAkisi)
class IsAkisiAdmin(admin.ModelAdmin):
    list_display = [
        'kod', 'ad', 'urun', 'versiyon', 'tip', 'operasyon_sayisi_goster', 
        'tahmini_sure_goster', 'aktif', 'olusturulma_tarihi'
    ]
    list_filter = ['tip', 'aktif', 'urun__kategori', 'olusturulma_tarihi']
    search_fields = ['kod', 'ad', 'urun__ad']
    readonly_fields = ['olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi']
    inlines = [IsAkisiOperasyonInline]
    
    def get_urls(self):
        """Custom URL'ler ekle"""
        urls = super().get_urls()
        custom_urls = [
            path('gorsel-tasarim/', self.admin_site.admin_view(self.gorsel_tasarim_view), 
                 name='production_isakisi_gorsel_tasarim'),
            path('<int:object_id>/gorsel-editor/', self.admin_site.admin_view(self.gorsel_editor_view), 
                 name='production_isakisi_gorsel_editor'),
            path('<int:object_id>/is-emirleri-olustur/', self.admin_site.admin_view(self.is_emirleri_olustur_view), 
                 name='production_isakisi_is_emirleri_olustur'),
            path('ajax/get-bom/<int:urun_id>/', self.admin_site.admin_view(self.ajax_get_bom), 
                 name='production_isakisi_ajax_get_bom'),
            path('ajax/save-workflow/', self.admin_site.admin_view(self.ajax_save_workflow), 
                 name='production_isakisi_ajax_save_workflow'),
        ]
        return custom_urls + urls
    
    def is_emirleri_olustur_view(self, request, object_id):
        """İş akışından otomatik iş emirleri oluştur"""
        is_akisi = get_object_or_404(IsAkisi, pk=object_id)
        
        if request.method == 'GET':
            # İş emri oluşturma formu göster
            context = {
                'title': f'{is_akisi.ad} - İş Emirleri Oluştur',
                'has_view_permission': True,
                'opts': self.model._meta,
                'is_akisi': is_akisi,
                'siparisler': Siparis.objects.filter(
                    sipariskalemi__urun=is_akisi.urun,
                    durum__in=['onaylandi', 'uretimde']
                ).distinct()
            }
            return render(request, 'admin/production/isakisi/is_emirleri_olustur.html', context)
        
        elif request.method == 'POST':
            # İş emirlerini oluştur
            try:
                siparis_id = request.POST.get('siparis')
                kalem_id = request.POST.get('kalem')
                miktar = int(request.POST.get('miktar', 1))
                baslangic_tarihi = request.POST.get('baslangic_tarihi')
                baslangic_saati = request.POST.get('baslangic_saati', '08:00')
                
                if not all([siparis_id, kalem_id, baslangic_tarihi]):
                    messages.error(request, 'Tüm alanları doldurun.')
                    return redirect(request.path)
                
                siparis = Siparis.objects.get(pk=siparis_id)
                kalem = SiparisKalem.objects.get(pk=kalem_id)
                
                # İş emirleri oluşturma
                self._create_work_orders_for_workflow(
                    is_akisi, siparis, kalem, miktar, 
                    baslangic_tarihi, baslangic_saati, request.user
                )
                
                messages.success(
                    request, 
                    f'{is_akisi.ad} iş akışı için {miktar} adetlik iş emirleri başarıyla oluşturuldu.'
                )
                return redirect('admin:production_isakisi_changelist')
                
            except Exception as e:
                messages.error(request, f'İş emirleri oluşturulurken hata: {str(e)}')
                return redirect(request.path)
    
    def _create_work_orders_for_workflow(self, is_akisi, siparis, kalem, miktar, 
                                        baslangic_tarihi, baslangic_saati, user):
        """İş akışı için otomatik iş emirleri oluştur"""
        from datetime import datetime, timedelta
        
        # Ana iş emri numarası
        ana_emir_no = f"AE-{siparis.siparis_no}-{is_akisi.kod}-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # İş akışındaki operasyonları sıralı al
        operasyonlar = is_akisi.operasyonlar.all().order_by('sira_no')
        
        if not operasyonlar.exists():
            raise ValueError("İş akışında operasyon bulunamadı!")
        
        # BOM gerekliliklerini belirle
        bom_malzemeleri = self._get_bom_requirements(is_akisi.urun, miktar)
        ara_urunler = self._get_sub_product_requirements(is_akisi.urun, miktar)
        
        # Başlangıç tarihi ve saati
        baslangic = datetime.strptime(f"{baslangic_tarihi} {baslangic_saati}", "%Y-%m-%d %H:%M")
        
        # Her operasyon için iş emri oluştur
        iş_emirleri = []
        for operasyon in operasyonlar:
            # Operasyon süresini hesapla
            planlanan_sure = float(operasyon.standart_sure or 0) + float(operasyon.hazirlik_suresi or 0)
            
            # Bitiş zamanını hesapla
            bitis = baslangic + timedelta(minutes=planlanan_sure)
            
            # İş emri oluştur
            is_emri = IsEmri.objects.create(
                emirNo=f"{ana_emir_no}-OP{operasyon.sira_no:02d}",
                ana_emirNo=ana_emir_no,
                siparis=siparis,
                siparis_kalemi=kalem,
                urun=is_akisi.urun,
                is_akisi=is_akisi,
                operasyon=operasyon,
                planlanan_miktar=miktar,
                planlanan_baslangic_tarihi=baslangic.date(),
                planlanan_baslangic_saati=baslangic.time(),
                planlanan_bitis_tarihi=bitis.date(),
                planlanan_bitis_saati=bitis.time(),
                planlanan_sure=planlanan_sure,
                gerekli_malzemeler=operasyon.operasyon_malzemeleri or [],
                gerekli_ara_urunler=operasyon.operasyon_ara_urunleri or [],
                olusturan=user
            )
            
            iş_emirleri.append(is_emri)
            
            # Sonraki operasyon için başlangıç zamanı
            baslangic = bitis
        
        # Operasyon bağımlılıklarını kur
        for i, is_emri in enumerate(iş_emirleri):
            if i > 0:
                is_emri.onceki_operasyonlar.add(iş_emirleri[i-1])
            
            # İş akışındaki bağımlılıkları da ekle
            for onceki_op in is_emri.operasyon.onceki_operasyonlar.all():
                onceki_emir = next((e for e in iş_emirleri if e.operasyon == onceki_op), None)
                if onceki_emir:
                    is_emri.onceki_operasyonlar.add(onceki_emir)
        
        return iş_emirleri
    
    def _get_bom_requirements(self, urun, miktar):
        """BOM gerekliliklerini getir"""
        requirements = []
        if hasattr(urun, 'recete'):
            for recete in urun.recete.all():
                requirements.append({
                    'malzeme': recete.malzeme.ad,
                    'miktar': float(recete.miktar * miktar),
                    'birim': recete.malzeme.birim,
                    'kategori': recete.malzeme.kategori
                })
        return requirements
    
    def _get_sub_product_requirements(self, urun, miktar):
        """Ara ürün gerekliliklerini getir"""
        requirements = []
        if hasattr(urun, 'recete'):
            for recete in urun.recete.all():
                if recete.malzeme.kategori == 'ara_urun':
                    requirements.append({
                        'ara_urun': recete.malzeme.ad,
                        'miktar': float(recete.miktar * miktar),
                        'birim': recete.malzeme.birim
                    })
        return requirements
    
    def gorsel_tasarim_view(self, request):
        """Görsel iş akışı tasarım sayfası"""
        context = {
            'title': 'Görsel İş Akışı Tasarımı',
            'has_view_permission': True,
            'opts': self.model._meta,
            'urunler': Urun.objects.filter(kategori__in=['bitmis_urun', 'ara_urun']).order_by('ad'),
            'standard_is_adimlari': StandardIsAdimi.objects.filter(aktif=True).order_by('kategori', 'ad'),
        }
        return render(request, 'admin/production/isakisi/gorsel_tasarim.html', context)
    
    def gorsel_editor_view(self, request, object_id):
        """Mevcut iş akışı için görsel editor"""
        is_akisi = get_object_or_404(IsAkisi, pk=object_id)
        
        # BOM bilgilerini al
        bom_items = []
        if is_akisi.urun and hasattr(is_akisi.urun, 'recete'):
            for recete in is_akisi.urun.recete.all():
                bom_items.append({
                    'urun': recete.malzeme.ad,
                    'miktar': recete.miktar,
                    'birim': recete.malzeme.birim,
                    'kategori': recete.malzeme.kategori
                })
        
        context = {
            'title': f'{is_akisi.ad} - Görsel Editor',
            'has_view_permission': True,
            'opts': self.model._meta,
            'is_akisi': is_akisi,
            'bom_items': bom_items,
            'standard_is_adimlari': StandardIsAdimi.objects.filter(aktif=True).order_by('kategori', 'ad'),
            'mevcut_operasyonlar': is_akisi.operasyonlar.all().order_by('sira_no'),
        }
        return render(request, 'admin/production/isakisi/gorsel_editor.html', context)
    
    def ajax_get_bom(self, request, urun_id):
        """AJAX ile BOM bilgilerini getir (recursif ara ürün desteği ile)"""
        try:
            urun = Urun.objects.get(pk=urun_id)
            bom_items = []
            
            if hasattr(urun, 'recete'):
                for recete in urun.recete.all():
                    malzeme = recete.malzeme
                    bom_item = {
                        'id': malzeme.id,
                        'ad': malzeme.ad,
                        'miktar': float(recete.miktar),
                        'birim': malzeme.birim,
                        'kategori': malzeme.get_kategori_display(),
                        'kategori_code': malzeme.kategori,
                        'stok': float(malzeme.stok_miktari) if malzeme.stok_miktari else 0,
                        'alt_malzemeler': []
                    }
                    
                    # Ara ürün ise kendi BOM'unu da ekle
                    if malzeme.kategori == 'ara_urun' and hasattr(malzeme, 'recete'):
                        for alt_recete in malzeme.recete.all():
                            alt_malzeme = alt_recete.malzeme
                            # Ara ürün başına gereken miktar ile alt malzeme miktarını çarp
                            alt_miktar = float(recete.miktar) * float(alt_recete.miktar)
                            
                            bom_item['alt_malzemeler'].append({
                                'id': alt_malzeme.id,
                                'ad': alt_malzeme.ad,
                                'miktar': alt_miktar,
                                'birim': alt_malzeme.birim,
                                'kategori': alt_malzeme.get_kategori_display(),
                                'kategori_code': alt_malzeme.kategori,
                                'stok': float(alt_malzeme.stok_miktari) if alt_malzeme.stok_miktari else 0
                            })
                    
                    bom_items.append(bom_item)
            
            return JsonResponse({
                'success': True,
                'bom_items': bom_items,
                'urun_ad': urun.ad
            })
            
        except Urun.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Ürün bulunamadı'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    def ajax_save_workflow(self, request):
        """AJAX ile görsel iş akışını kaydet"""
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Sadece POST desteklenir'})
        
        try:
            import json
            data = json.loads(request.body)
            
            # Gerekli veriler
            workflow_data = data.get('workflow', {})
            urun_id = workflow_data.get('urun_id')
            workflow_name = workflow_data.get('name', 'Yeni İş Akışı')
            workflow_code = workflow_data.get('code', f'WF-{timezone.now().strftime("%Y%m%d-%H%M%S")}')
            steps = data.get('steps', [])
            connections = data.get('connections', [])
            
            if not urun_id:
                return JsonResponse({'success': False, 'error': 'Ürün seçimi gerekli'})
            
            if not steps:
                return JsonResponse({'success': False, 'error': 'En az bir adım gerekli'})
            
            # Transaction içinde işlem yap
            with transaction.atomic():
                # İş akışını oluştur
                urun = Urun.objects.get(pk=urun_id)
                is_akisi = IsAkisi.objects.create(
                    kod=workflow_code,
                    ad=workflow_name,
                    urun=urun,
                    tip='seri',  # Varsayılan olarak seri
                    olusturan=request.user
                )
                
                # Operasyonları oluştur
                step_mapping = {}  # Canvas ID'leri ile veritabanı ID'lerini eşleştir
                
                for step in steps:
                    step_type = step.get('type')
                    if step_type == 'standard':  # Standard iş adımları
                        standard_step = StandardIsAdimi.objects.get(pk=step.get('standard_id'))
                        
                        # İstasyonu bul (gerekli istasyon tipine göre)
                        istasyon = IsIstasyonu.objects.filter(
                            tip=standard_step.gerekli_istasyon_tipi,
                            aktif=True
                        ).first()
                        
                        if not istasyon:
                            # Yoksa generic istasyon oluştur
                            istasyon = IsIstasyonu.objects.create(
                                kod=f"IST-{standard_step.gerekli_istasyon_tipi.upper()}",
                                ad=f"Genel {standard_step.get_gerekli_istasyon_tipi_display()}",
                                tip=standard_step.gerekli_istasyon_tipi,
                                aktif=True,
                                olusturan=request.user
                            )
                        
                        # Operasyon için malzeme ve ara ürün gerekliliklerini hesapla
                        step_materials = step.get('materials', [])
                        step_subproducts = step.get('subproducts', [])
                        
                        # Malzeme atamaları sessizce işleniyor
                        
                        operasyon = IsAkisiOperasyon.objects.create(
                            is_akisi=is_akisi,
                            operasyon_adi=standard_step.ad,
                            istasyon=istasyon,
                            standart_sure=standard_step.tahmini_sure_birim,
                            hazirlik_suresi=0,
                            kalite_kontrolu_gerekli=False,
                            kritik=False,
                            operasyon_malzemeleri=step_materials,
                            operasyon_ara_urunleri=step_subproducts,
                            aciklama=f"Otomatik oluşturuldu: {standard_step.kod}"
                        )
                        
                        step_mapping[step.get('id')] = operasyon
                
                # Bağımlılıkları kur
                for conn in connections:
                    from_step = step_mapping.get(conn.get('from'))
                    to_step = step_mapping.get(conn.get('to'))
                    
                    if from_step and to_step:
                        to_step.onceki_operasyonlar.add(from_step)
                
                return JsonResponse({
                    'success': True,
                    'workflow_id': is_akisi.id,
                    'workflow_name': is_akisi.ad,
                    'workflow_code': is_akisi.kod,
                    'message': f'İş akışı "{is_akisi.ad}" başarıyla kaydedildi!'
                })
                
        except Urun.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ürün bulunamadı'})
        except StandardIsAdimi.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Standard iş adımı bulunamadı'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ürün seçimini bitmiş ürün ve ara ürünle sınırla"""
        if db_field.name == "urun":
            kwargs["queryset"] = Urun.objects.filter(
                kategori__in=['bitmis_urun', 'ara_urun']
            ).order_by('ad')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('kod', 'ad', 'urun', 'versiyon', 'aciklama')
        }),
        ('Akış Ayarları', {
            'fields': ('tip', 'aktif')
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def operasyon_sayisi_goster(self, obj):
        """Operasyon sayısını göster"""
        sayi = obj.toplam_operasyon_sayisi
        kritik_sayi = obj.operasyonlar.filter(kritik=True).count()
        
        return format_html(
            '<strong>{}</strong> <small>({} kritik)</small>',
            sayi, kritik_sayi
        )
    operasyon_sayisi_goster.short_description = 'Operasyon Sayısı'
    
    def tahmini_sure_goster(self, obj):
        """Tahmini süreyi göster"""
        sure = obj.tahmini_sure
        saat = int(sure // 60)
        dakika = int(sure % 60)
        
        if saat > 0:
            return format_html(
                '<strong>{}s {}dk</strong> <small>({})</small>',
                saat, dakika, obj.get_tip_display()
            )
        else:
            return format_html(
                '<strong>{}dk</strong> <small>({})</small>',
                dakika, obj.get_tip_display()
            )
    tahmini_sure_goster.short_description = 'Tahmini Süre'
    
    def save_model(self, request, obj, form, change):
        """Kaydet sırasında kullanıcıyı ata"""
        if not change:
            obj.olusturan = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Operasyon kaydetme sırasında sıra no ata"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, IsAkisiOperasyon):
                if not instance.sira_no or instance.sira_no == 0:
                    # Bu iş akışındaki en büyük sıra no'yu bul
                    max_sira = IsAkisiOperasyon.objects.filter(
                        is_akisi=form.instance
                    ).aggregate(
                        max_sira=models.Max('sira_no')
                    )['max_sira']
                    
                    instance.sira_no = (max_sira or 0) + 1
                    instance.is_akisi = form.instance
            instance.save()
        formset.save_m2m()
        super().save_formset(request, form, formset, change)


@admin.register(IsAkisiOperasyon)
class IsAkisiOperasyonAdmin(admin.ModelAdmin):
    list_display = [
        'is_akisi', 'sira_no', 'operasyon_adi', 'istasyon', 
        'standart_sure', 'toplam_sure_goster', 'kritik', 'bagimlillik_goster'
    ]
    list_filter = ['kritik', 'kalite_kontrolu_gerekli', 'istasyon__tip', 'is_akisi__urun']
    search_fields = ['operasyon_adi', 'is_akisi__ad', 'istasyon__ad']
    raw_id_fields = ['onceki_operasyonlar']
    readonly_fields = ['sira_no', 'bagimlillik_detay']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('is_akisi', 'sira_no', 'operasyon_adi', 'istasyon', 'aciklama')
        }),
        ('Süre Bilgileri', {
            'fields': ('standart_sure', 'hazirlik_suresi')
        }),
        ('Kontrol ve Kritiklik', {
            'fields': ('kalite_kontrolu_gerekli', 'kritik')
        }),
        ('Malzeme Gereklilikleri', {
            'fields': ('operasyon_malzemeleri', 'operasyon_ara_urunleri'),
            'description': 'Bu operasyonda kullanılacak spesifik malzeme ve ara ürünleri tanımlayın',
            'classes': ('collapse',)
        }),
        ('Bağımlılıklar', {
            'fields': ('onceki_operasyonlar', 'bagimlillik_detay'),
            'description': 'Bu operasyondan önce tamamlanması gereken operasyonları seçin'
        }),
    )
    
    def toplam_sure_goster(self, obj):
        """Toplam süreyi göster"""
        toplam = obj.toplam_sure
        return format_html(
            '<strong>{}dk</strong> <small>(H:{} + S:{})</small>',
            toplam, obj.hazirlik_suresi, obj.standart_sure
        )
    toplam_sure_goster.short_description = 'Toplam Süre'
    
    def bagimlillik_goster(self, obj):
        """Bağımlılık sayısını göster"""
        sayi = obj.onceki_operasyon_sayisi
        if sayi > 0:
            return format_html(
                '<span style="color: #ffc107;">⚠️ {} bağımlılık</span>',
                sayi
            )
        return format_html('<span style="color: #28a745;">✅ Bağımlılık yok</span>')
    bagimlillik_goster.short_description = 'Bağımlılık'
    
    def bagimlillik_detay(self, obj):
        """Bağımlılık detayını göster"""
        if obj.pk:
            bagimlilıklar = obj.onceki_operasyonlar.all()
            if bagimlilıklar:
                detay_list = []
                for b in bagimlilıklar:
                    detay_list.append(
                        f"<li><strong>{b.sira_no:02d}. {b.operasyon_adi}</strong><br>"
                        f"<small>İstasyon: {b.istasyon} | Süre: {b.standart_sure}dk</small></li>"
                    )
                return format_html(
                    '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
                    ''.join(detay_list)
                )
            return format_html('<em style="color: #999;">Bu operasyonun bağımlılığı yok</em>')
        return format_html('<em style="color: #999;">Kaydet sonrası görünür</em>')
    bagimlillik_detay.short_description = 'Bağımlılık Detayı'




class IsEmriAdminForm(forms.ModelForm):
    class Meta:
        model = IsEmri
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Akıllı filtreleme: sadece mantıklı bağımlılıkları göster
            self.fields['onceki_operasyonlar'].queryset = self._get_valid_dependencies_queryset()
    
    def _get_valid_dependencies_queryset(self):
        """Bu iş emri için mantıklı bağımlılıkları getir"""
        instance = self.instance
        valid_emirler = []
        
        # Ana ürün iş emri ise
        if instance.urun.kategori == 'bitmis_urun':
            # Ana ürünün ilk operasyonu ise - ara ürünleri göster
            ana_urun_emirleri = IsEmri.objects.filter(
                siparis=instance.siparis,
                urun=instance.urun
            ).order_by('operasyon__sira_no')
            
            if ana_urun_emirleri.first() == instance:
                # İlk operasyon - sadece ara ürün emirleri
                valid_emirler = IsEmri.objects.filter(
                    siparis=instance.siparis,
                    urun__kategori='ara_urun'
                )
            else:
                # Diğer operasyonlar - sadece önceki ana ürün operasyonu
                onceki_emir = IsEmri.objects.filter(
                    siparis=instance.siparis,
                    urun=instance.urun,
                    operasyon__sira_no__lt=instance.operasyon.sira_no
                ).order_by('operasyon__sira_no').last()
                
                if onceki_emir:
                    valid_emirler = IsEmri.objects.filter(pk=onceki_emir.pk)
                else:
                    valid_emirler = IsEmri.objects.none()
        
        # Ara ürün iş emri ise
        elif instance.urun.kategori == 'ara_urun':
            # Aynı ara ürünün önceki operasyonu (varsa)
            onceki_emir = IsEmri.objects.filter(
                siparis=instance.siparis,
                urun=instance.urun,
                operasyon__sira_no__lt=instance.operasyon.sira_no
            ).order_by('operasyon__sira_no').last()
            
            if onceki_emir:
                valid_emirler = IsEmri.objects.filter(pk=onceki_emir.pk)
            else:
                # İlk operasyon - bağımlılık yok
                valid_emirler = IsEmri.objects.none()
        
        else:
            # Hammadde vs. - bağımlılık yok  
            valid_emirler = IsEmri.objects.none()
            
        return valid_emirler.order_by('urun__ad', 'operasyon__sira_no')

@admin.register(IsEmri)
class IsEmriAdmin(admin.ModelAdmin):
    form = IsEmriAdminForm
    list_display = [
        'emirNo', 'ana_emirNo', 'operasyon', 'siparis', 'urun', 'durum_renkli', 'oncelik_renkli',
        'planlanan_miktar', 'tamamlanma_goster', 'planlanan_baslangic_tarihi',
        'gecikme_goster', 'sorumlu'
    ]
    list_filter = [
        'durum', 'oncelik', 'urun__kategori', 'is_akisi', 
        'planlanan_baslangic_tarihi', 'olusturulma_tarihi', 'operasyon__istasyon'
    ]
    search_fields = ['emirNo', 'ana_emirNo', 'siparis__siparis_no', 'urun__ad', 'operasyon__operasyon_adi']
    readonly_fields = ['emirNo', 'olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi']
    # actions = ['bagimlilik_duzelt_action']  # Artık gerekli değil - bağımlılıklar otomatik doğru kuruluyor
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('emirNo', 'ana_emirNo', 'siparis', 'siparis_kalemi', 'urun', 'is_akisi', 'operasyon')
        }),
        ('Miktar ve Hedefler', {
            'fields': ('planlanan_miktar', 'uretilen_miktar')
        }),
        ('Planlama Tarihleri', {
            'fields': (
                ('planlanan_baslangic_tarihi', 'planlanan_baslangic_saati'),
                ('planlanan_bitis_tarihi', 'planlanan_bitis_saati'),
                'planlanan_sure'
            )
        }),
        ('Gerçekleşen Tarihleri', {
            'fields': (
                ('gercek_baslangic_tarihi', 'gercek_baslangic_saati'),
                ('gercek_bitis_tarihi', 'gercek_bitis_saati'),
                'gercek_sure'
            ),
            'classes': ('collapse',)
        }),
        ('Durum ve Gereklilikler', {
            'fields': ('durum', 'oncelik', 'gerekli_malzemeler', 'gerekli_ara_urunler', 'onceki_operasyonlar')
        }),
        ('Sorumlu ve Notlar', {
            'fields': ('sorumlu', 'aciklama', 'notlar')
        }),
        ('Sistem Bilgileri', {
            'fields': ('olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    # Eski bağımlılık düzeltme action'ları kaldırıldı - artık otomatik doğru kuruluyor
    
    def durum_renkli(self, obj):
        """Renk kodlu durum"""
        durum_emoji = {
            'planlandi': '📋',
            'basladi': '▶️',
            'devam_ediyor': '⚙️',
            'beklemede': '⏸️',
            'tamamlandi': '✅',
            'iptal': '❌'
        }
        emoji = durum_emoji.get(obj.durum, '❓')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            obj.durum_renk, emoji, obj.get_durum_display()
        )
    durum_renkli.short_description = 'Durum'
    
    def oncelik_renkli(self, obj):
        """Renk kodlu öncelik"""
        oncelik_emoji = {
            'dusuk': '⬇️',
            'normal': '➡️',
            'yuksek': '⬆️',
            'acil': '🚨'
        }
        emoji = oncelik_emoji.get(obj.oncelik, '➡️')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            obj.oncelik_renk, emoji, obj.get_oncelik_display()
        )
    oncelik_renkli.short_description = 'Öncelik'
    
    def tamamlanma_goster(self, obj):
        """Tamamlanma oranı göster"""
        oran = obj.tamamlanma_orani
        return format_html(
            '<div style="width: 80px; background: #f0f0f0; border-radius: 10px; padding: 2px;">'
            '<div style="width: {}%; background: {}; height: 16px; border-radius: 8px; text-align: center; color: white; font-size: 10px; line-height: 16px;">'
            '{}%</div></div>',
            oran, obj.durum_renk, int(oran)
        )
    tamamlanma_goster.short_description = 'Tamamlanma'
    
    def gecikme_goster(self, obj):
        """Gecikme durumu göster"""
        durum = obj.gecikme_durumu
        if durum == 'zamaninda':
            return format_html('<span style="color: #28a745;">✅ Zamanında</span>')
        elif durum == 'gecikmede':
            return format_html('<span style="color: #ffc107;">⚠️ Gecikmede</span>')
        else:  # gecikti
            return format_html('<span style="color: #dc3545;">🚫 Gecikti</span>')
    gecikme_goster.short_description = 'Gecikme'
    
    
    def save_model(self, request, obj, form, change):
        """İş emri kaydetme işlemleri"""
        if not change:
            obj.olusturan = request.user
        
        super().save_model(request, obj, form, change)


    