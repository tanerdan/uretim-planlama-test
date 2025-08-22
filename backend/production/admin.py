# backend/production/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, F
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
    readonly_fields = ['malzeme_ihtiyaci', 'miktar', 'birim_fiyat', 'toplam_fiyat']

class SatinAlmaTeslimGuncellemeInline(admin.TabularInline):
    model = SatinAlmaTeslimGuncelleme
    extra = 0
    readonly_fields = ['eski_teslim_tarihi', 'guncelleyen', 'guncelleme_tarihi']
    fields = ['eski_teslim_tarihi', 'yeni_teslim_tarihi', 'aciklama', 'guncelleyen', 'guncelleme_tarihi']
    can_delete = False

@admin.register(SatinAlmaSiparisi)
class SatinAlmaSiparisiAdmin(admin.ModelAdmin):
    list_display = ['siparis_no', 'tedarikci', 'tarih', 'teslim_tarihi', 'guncel_teslim_tarihi', 'toplam_tutar', 'olusturan']
    list_editable = ['guncel_teslim_tarihi']
    change_form_template = 'admin/change_form_satinalma.html'
    list_filter = ['tarih', 'tedarikci']
    search_fields = ['siparis_no', 'tedarikci__ad']
    readonly_fields = ['siparis_no', 'olusturan', 'olusturulma_tarihi']
    inlines = [SatinAlmaKalemiInline, SatinAlmaTeslimGuncellemeInline]
    
    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('siparis_no', 'tedarikci', 'tarih', 'teslim_tarihi', 'guncel_teslim_tarihi', 'toplam_tutar')
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

@admin.register(MalzemeGelis)
class MalzemeGelisAdmin(admin.ModelAdmin):
    list_display = [
        'satinalma_siparisi', 'malzeme_adi', 'gelen_miktar', 
        'birim_fiyat', 'para_birimi', 'toplam_tutar',
        'gelis_tarihi', 'irsaliye_no', 'kaydeden'
    ]
    list_filter = ['gelis_tarihi', 'kayit_tarihi']
    search_fields = [
        'satinalma_siparisi__siparis_no', 
        'satinalma_kalemi__malzeme_ihtiyaci__malzeme_adi',
        'irsaliye_no', 'fatura_no'
    ]
    readonly_fields = ['kayit_tarihi', 'kaydeden', 'toplam_tutar']
    date_hierarchy = 'gelis_tarihi'
    ordering = ['-gelis_tarihi', '-kayit_tarihi']
    
    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('satinalma_siparisi', 'satinalma_kalemi')
        }),
        ('Geliş Bilgileri', {
            'fields': ('gelen_miktar', 'gelis_tarihi')
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
        return obj.satinalma_kalemi.malzeme_ihtiyaci.malzeme_adi
    malzeme_adi.short_description = 'Malzeme Adı'
    
    def save_model(self, request, obj, form, change):
        """Kaydetme sırasında kullanıcıyı otomatik ata"""
        if not change:  # Yeni kayıtsa
            obj.kaydeden = request.user
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """İlişkili alanlar için filtreler"""
        if db_field.name == "satinalma_kalemi":
            # Önce sipariş seçilmişse sadece o siparişin kalemlerini göster
            siparis_id = request.GET.get('satinalma_siparisi')
            if siparis_id:
                kwargs["queryset"] = SatinAlmaKalemi.objects.filter(
                    siparis_id=siparis_id
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Üretim Planlama için proxy model
class UretimPlanlama(IsEmri):
    class Meta:
        proxy = True
        verbose_name = "Üretim Planlaması"
        verbose_name_plural = "Üretim Planlaması"

# ÜRETIM MODÜLÜ ADMIN'LERİ

@admin.register(StandardIsAdimi)
class StandardIsAdimiAdmin(admin.ModelAdmin):
    list_display = ['ad', 'kategori', 'tahmini_sure_birim', 'aktif']
    search_fields = ['ad', 'aciklama']
    list_filter = ['kategori', 'aktif']

@admin.register(IsIstasyonu) 
class IsIstasyonuAdmin(admin.ModelAdmin):
    list_display = ['ad', 'tip', 'lokasyon', 'aktif']
    list_filter = ['aktif', 'tip']
    search_fields = ['ad', 'aciklama']

@admin.register(IsAkisi)
class IsAkisiAdmin(admin.ModelAdmin):
    list_display = ['ad', 'urun', 'versiyon', 'operasyon_sayisi']
    list_filter = ['urun__kategori']
    search_fields = ['ad', 'urun__ad']
    
    def operasyon_sayisi(self, obj):
        return obj.operasyonlar.count()
    operasyon_sayisi.short_description = 'Operasyon Sayısı'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/gorsel-tasarim/', self.admin_site.admin_view(self.gorsel_tasarim_view), name='production_isakisi_gorsel_tasarim'),
        ]
        return custom_urls + urls

    def gorsel_tasarim_view(self, request, object_id):
        """Görsel iş akışı tasarım sayfası"""
        is_akisi = get_object_or_404(IsAkisi, pk=object_id)
        
        if request.method == 'POST':
            try:
                workflow_data = request.POST.get('workflow_data')
                if workflow_data:
                    workflow = json.loads(workflow_data)
                    
                    # Mevcut operasyonları temizle
                    is_akisi.operasyonlar.all().delete()
                    
                    # Yeni operasyonları kaydet
                    for op_data in workflow['operations']:
                        IsAkisiOperasyon.objects.create(
                            is_akisi=is_akisi,
                            operasyon_id=op_data['operasyon_id'],
                            sira_no=op_data['sira_no'],
                            konum_x=op_data['x'],
                            konum_y=op_data['y'],
                            malzeme_atamalari=json.dumps(op_data.get('malzemeler', []))
                        )
                    
                    return JsonResponse({'success': True})
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        context = {
            'title': f'{is_akisi.urun.ad} - Görsel İş Akışı Tasarımı',
            'is_akisi': is_akisi,
            'standard_adimlar': StandardIsAdimi.objects.all(),
            'bom_malzemeleri': [],
            'mevcut_operasyonlar': is_akisi.operasyonlar.all(),
            'opts': self.model._meta,
        }
        
        if is_akisi.urun.recete.exists():
            context['bom_malzemeleri'] = is_akisi.urun.recete.all()
        
        return render(request, 'admin/production/isakisi/gorsel_tasarim.html', context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """İş akışı detay sayfasında görsel tasarım butonunu göster"""
        extra_context = extra_context or {}
        extra_context['gorsel_tasarim_url'] = reverse('admin:production_isakisi_gorsel_tasarim', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

@admin.register(IsAkisiOperasyon)
class IsAkisiOperasyonAdmin(admin.ModelAdmin):
    list_display = ['is_akisi', 'istasyon', 'operasyon_adi', 'sira_no']
    list_filter = ['is_akisi__urun__kategori']
    search_fields = ['is_akisi__urun__ad', 'istasyon__ad']
    

# İş Emri Admin'leri
from django import forms

class IsEmriAdminForm(forms.ModelForm):
    class Meta:
        model = IsEmri
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'siparis_kalemi' in self.data:
            try:
                siparis_kalemi_id = int(self.data.get('siparis_kalemi'))
                siparis_kalemi = SiparisKalem.objects.get(id=siparis_kalemi_id)
                self.fields['urun'].queryset = Urun.objects.filter(id=siparis_kalemi.urun.id)
                self.fields['is_akisi'].queryset = IsAkisi.objects.filter(urun=siparis_kalemi.urun)
            except (ValueError, SiparisKalem.DoesNotExist):
                self.fields['urun'].queryset = Urun.objects.none()
                self.fields['is_akisi'].queryset = IsAkisi.objects.none()
        elif self.instance.pk:
            if self.instance.siparis_kalemi:
                self.fields['urun'].queryset = Urun.objects.filter(id=self.instance.siparis_kalemi.urun.id)
                self.fields['is_akisi'].queryset = IsAkisi.objects.filter(urun=self.instance.siparis_kalemi.urun)
        else:
            self.fields['urun'].queryset = Urun.objects.none()
            self.fields['is_akisi'].queryset = IsAkisi.objects.none()

class IsEmriAdmin(admin.ModelAdmin):
    form = IsEmriAdminForm
    list_display = [
        'emirNo', 'ana_emirNo', 'operasyon', 'siparis', 'urun', 'durum_renkli', 'oncelik_renkli',
        'planlanan_miktar', 'tamamlanma_goster', 'planlanan_baslangic_tarihi',
        'planlanan_istasyon', 'gecikme_goster'
    ]
    list_filter = ['durum', 'oncelik', 'planlanan_baslangic_tarihi', 'olusturulma_tarihi']
    search_fields = ['emirNo', 'siparis_kalemi__siparis__siparis_no', 'urun__ad']
    readonly_fields = ['emirNo', 'olusturan', 'olusturulma_tarihi', 'guncellenme_tarihi']
    
    def durum_renkli(self, obj):
        renkler = {
            'planlandi': '#007cba',
            'malzeme_bekliyor': '#ffc107', 
            'ara_urun_bekliyor': '#fd7e14',
            'hazir': '#28a745',
            'basladi': '#17a2b8',
            'devam_ediyor': '#6f42c1',
            'beklemede': '#6c757d',
            'tamamlandi': '#28a745',
            'iptal': '#dc3545'
        }
        renk = renkler.get(obj.durum, '#6c757d')
        durum_text = str(obj.get_durum_display())  # SafeString'i string'e çevir
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            renk, durum_text
        )
    durum_renkli.short_description = 'Durum'
    
    def oncelik_renkli(self, obj):
        renkler = {
            'dusuk': '#28a745',
            'normal': '#007cba',
            'yuksek': '#ffc107',
            'acil': '#dc3545'
        }
        renk = renkler.get(obj.oncelik, '#6c757d')
        oncelik_text = str(obj.get_oncelik_display())  # SafeString'i string'e çevir
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            renk, oncelik_text
        )
    oncelik_renkli.short_description = 'Öncelik'
    
    def siparis(self, obj):
        if obj.siparis_kalemi and obj.siparis_kalemi.siparis:
            return obj.siparis_kalemi.siparis.siparis_no
        return "-"
    siparis.short_description = 'Sipariş No'
    
    def tamamlanma_goster(self, obj):
        if obj.planlanan_miktar > 0:
            oran = (obj.uretilen_miktar / obj.planlanan_miktar) * 100
        else:
            oran = 0
        
        # Renk sabit olarak yeşil kullanıyoruz
        oran_str = f"{oran:.0f}%"
        return format_html(
            '<div style="background: linear-gradient(to right, #28a745 {}%, #f0f0f0 {}%); '
            'padding: 2px 5px; border-radius: 3px; font-size: 11px;">{}</div>',
            int(oran), int(oran), oran_str
        )
    tamamlanma_goster.short_description = 'Tamamlanma'
    
    def gecikme_goster(self, obj):
        try:
            durum = obj.gecikme_durumu
            if durum == 'zamaninda':
                return format_html('<span style="color: #28a745;">✅ Zamanında</span>')
            elif durum == 'gecikmede':
                return format_html('<span style="color: #ffc107;">⚠️ Gecikmede</span>')
            else:
                return format_html('<span style="color: #dc3545;">🚫 Gecikti</span>')
        except:
            return "-"
    gecikme_goster.short_description = 'Gecikme'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.olusturan = request.user
        super().save_model(request, obj, form, change)
    
    # Toplu İşlemler
    actions = ['reset_durum_malzeme_bekliyor', 'reset_planlanan_istasyon']
    
    def reset_durum_malzeme_bekliyor(self, request, queryset):
        """Seçilen iş emirlerinin durumunu 'malzeme_bekliyor' olarak değiştir"""
        updated = queryset.update(durum='malzeme_bekliyor')
        self.message_user(request, f'{updated} iş emrinin durumu malzeme_bekliyor olarak güncellendi.')
    reset_durum_malzeme_bekliyor.short_description = "Durumu 'Malzeme Bekliyor' yap"
    
    def reset_planlanan_istasyon(self, request, queryset):
        """Seçilen iş emirlerinin planlanan istasyonunu temizle"""
        from datetime import date
        updated = queryset.update(
            planlanan_istasyon=None, 
            planlanan_baslangic_tarihi=date.today()
        )
        self.message_user(request, f'{updated} iş emrinin planlanan istasyonu temizlendi.')
    reset_planlanan_istasyon.short_description = "Planlanan istasyonu temizle"

class UretimPlanlamaAdmin(admin.ModelAdmin):
    """Üretim Planlama - Ana planlama ekranı"""
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def changelist_view(self, request, extra_context=None):
        """Ana üretim planlama ekranı - Gantt görünümü"""
        from datetime import datetime, timedelta
        import calendar
        
        # İş istasyonlarını özel sıralama ile getir
        def istasyon_sirala_key(istasyon):
            """İstasyon adına göre sıralama anahtarı"""
            ad = istasyon.ad.lower()
            
            # AG Sargı'lar en önce (1xx)
            if 'ag' in ad and 'sargı' in ad:
                return (100, ad)
            # YG Sargı'lar ikinci sırada (2xx)  
            elif 'yg' in ad and 'sargı' in ad:
                return (200, ad)
            # Montaj üçüncü sırada (3xx)
            elif 'montaj' in ad:
                return (300, ad)
            # Kurutma dördüncü sırada (4xx)
            elif 'kurutma' in ad:
                return (400, ad)
            # Test beşinci sırada (5xx)
            elif 'test' in ad:
                return (500, ad)
            # Diğerleri en sonda (9xx)
            else:
                return (900, ad)
        
        # Tüm aktif istasyonları al ve sırala
        istasyonlar = list(IsIstasyonu.objects.filter(aktif=True))
        istasyonlar.sort(key=istasyon_sirala_key)
        
        # Günleri hazırla (bugünden itibaren 30 gün)
        bugun = datetime.now().date()
        gunler = []
        for i in range(30):
            gun = bugun + timedelta(days=i)
            gun_adi = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'][gun.weekday()]
            # Çalışma saati: Pazartesi-Cuma 9 saat, Cumartesi-Pazar 0 saat
            default_calisma_saati = 9 if gun.weekday() < 5 else 0
            gunler.append({
                'tarih': gun,
                'gun_adi': gun_adi,
                'is_today': gun == bugun,
                'is_weekend': gun.weekday() >= 5,  # Cumartesi=5, Pazar=6
                'default_calisma_saati': default_calisma_saati
            })
        
        # Planlanmamış iş emirlerini getir
        planlanmamis_emirler = IsEmri.objects.filter(
            planlanan_istasyon__isnull=True,
            durum__in=['planlandi', 'malzeme_bekliyor', 'hazir']
        ).select_related(
            'siparis_kalemi__siparis__musteri',
            'urun',
            'operasyon'
        ).order_by('siparis_kalemi__siparis__siparis_no', 'operasyon__sira_no')
        
        # Planlanmış iş emirlerini getir
        planlanmis_emirler = IsEmri.objects.filter(
            planlanan_istasyon__isnull=False
        ).select_related(
            'siparis_kalemi__siparis__musteri',
            'urun',
            'operasyon',
            'planlanan_istasyon'
        ).order_by('planlanan_baslangic_tarihi')
        
        # Planlanmış emirler için de süre hesaplama
        for emir in planlanmis_emirler:
            # Süre hesaplama - miktar ile çarp
            if not emir.planlanan_sure and emir.operasyon:
                # Planlanan süre yoksa operasyonun standart süresini kullan
                birim_sure = emir.operasyon.toplam_sure() if hasattr(emir.operasyon, 'toplam_sure') else 60
            else:
                birim_sure = float(emir.planlanan_sure or 60)
            
            # Toplam süre = birim süre × miktar
            miktar = float(emir.planlanan_miktar or 1)
            emir.hesaplanan_sure = birim_sure * miktar
            
            # Saate çevir (dakikadan saate)
            emir.hesaplanan_sure_saat = round(emir.hesaplanan_sure / 60, 1)
        
        # Sipariş bazında gruplama (planlanmamış emirler için)
        siparis_emirleri = defaultdict(list)
        for emir in planlanmamis_emirler:
            if emir.siparis_kalemi and emir.siparis_kalemi.siparis:
                siparis_no = emir.siparis_kalemi.siparis.siparis_no
                siparis_emirleri[siparis_no].append(emir)
            else:
                # Ara ürün veya sipariş kalemi olmayan iş emirleri
                siparis_emirleri['Ara Ürünler'].append(emir)
        
        # Her emir için bağımlılıkları ve süre bilgilerini hesapla
        for emirler_listesi in siparis_emirleri.values():
            for emir in emirler_listesi:
                # Bu emirden önceki adımları bul (sıra numarasına göre)
                emir.onceki_adimlar = []
                if emir.operasyon and emir.siparis_kalemi:
                    # Aynı sipariş kalemindeki daha küçük sıra numaralı operasyonları bul
                    onceki_emirler = IsEmri.objects.filter(
                        siparis_kalemi=emir.siparis_kalemi,
                        operasyon__sira_no__lt=emir.operasyon.sira_no
                    ).select_related('operasyon').order_by('operasyon__sira_no')
                    
                    for onceki_emir in onceki_emirler:
                        emir.onceki_adimlar.append({
                            'emir': onceki_emir,
                            'durum': onceki_emir.durum,
                            'tamamlandi': onceki_emir.durum == 'tamamlandi'
                        })
                
                # Süre hesaplama - miktar ile çarp
                if not emir.planlanan_sure and emir.operasyon:
                    # Planlanan süre yoksa operasyonun standart süresini kullan
                    birim_sure = emir.operasyon.toplam_sure() if hasattr(emir.operasyon, 'toplam_sure') else 60
                else:
                    birim_sure = float(emir.planlanan_sure or 60)
                
                # Toplam süre = birim süre × miktar
                miktar = float(emir.planlanan_miktar or 1)
                emir.hesaplanan_sure = birim_sure * miktar
                
                # Saate çevir (dakikadan saate)
                emir.hesaplanan_sure_saat = round(emir.hesaplanan_sure / 60, 1)
        
        context = {
            'title': 'Üretim Planlama',
            'istasyonlar': istasyonlar,
            'gunler': gunler,
            'planlanmamis_emirler': planlanmamis_emirler,
            'planli_emirler': planlanmis_emirler,
            'siparis_emirleri': dict(siparis_emirleri),
            'opts': UretimPlanlama._meta,
            'app_label': UretimPlanlama._meta.app_label,
        }
        
        return render(request, 'admin/production/uretim_planlama_gantt.html', context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('planlama/', self.admin_site.admin_view(self.planlama_view), name='production_uretimplanlama_planlama'),
            path('emir-guncelle/', self.admin_site.admin_view(self.emir_guncelle_view), name='production_uretimplanlama_emir_guncelle'),
            path('update-planning/', self.admin_site.admin_view(self.update_planning_view), name='production_uretimplanlama_update_planning'),
            path('unplan-order/', self.admin_site.admin_view(self.unplan_order_view), name='production_uretimplanlama_unplan_order'),
        ]
        return custom_urls + urls
    
    def planlama_view(self, request):
        return self.changelist_view(request)
    
    def unplan_order_view(self, request):
        """İş emrinin planlamasını kaldır"""
        if request.method == 'POST':
            try:
                import json
                data = json.loads(request.body)
                order_id = data.get('order_id')
                
                if not order_id:
                    return JsonResponse({'success': False, 'error': 'order_id gerekli'})
                
                # İş emrini bul
                try:
                    emir = IsEmri.objects.get(id=order_id)
                except IsEmri.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'İş emri bulunamadı'})
                
                # Planlamayı kaldır
                from django.utils import timezone
                emir.planlanan_istasyon = None
                # Eğer field null=False ise bugünün tarihini koy, null=True ise None
                try:
                    emir.planlanan_baslangic_tarihi = None
                    emir.save()
                except:
                    # NULL constraint hatası varsa bugünün tarihini koy
                    emir.planlanan_baslangic_tarihi = timezone.now().date()
                    emir.save()
                
                return JsonResponse({'success': True})
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Sadece POST istekleri kabul edilir'})
    
    def update_planning_view(self, request):
        """Gantt görünümünde drag & drop için AJAX endpoint"""
        if request.method == 'POST':
            import json
            from datetime import datetime
            
            try:
                data = json.loads(request.body)
                order_id = data.get('order_id')
                station_id = data.get('station_id') 
                date_str = data.get('date')
                
                # İş emrini bul
                emir = get_object_or_404(IsEmri, id=order_id)
                
                # İstasyonu bul
                istasyon = get_object_or_404(IsIstasyonu, id=station_id)
                
                # Tarihi parse et
                planlanan_tarih = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # İş emrini güncelle
                emir.planlanan_istasyon = istasyon
                emir.planlanan_baslangic_tarihi = planlanan_tarih
                # emir.durum = 'planlandi'  # Durum değiştirme şimdilik yapılmasın
                emir.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'İş emri {istasyon.ad} istasyonuna {planlanan_tarih.strftime("%d.%m.%Y")} tarihinde planlandı.'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'error': str(e)
                })
        
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    def emir_guncelle_view(self, request):
        if request.method == 'POST':
            try:
                emir_id = request.POST.get('emir_id')
                istasyon_id = request.POST.get('istasyon_id')
                planlanan_tarih = request.POST.get('planlanan_tarih')
                
                emir = get_object_or_404(IsEmri, id=emir_id)
                
                if istasyon_id:
                    istasyon = get_object_or_404(IsIstasyonu, id=istasyon_id)
                    emir.planlanan_istasyon = istasyon
                
                if planlanan_tarih:
                    from datetime import datetime
                    emir.planlanan_baslangic_tarihi = datetime.fromisoformat(planlanan_tarih)
                
                emir.save()
                
                return JsonResponse({'success': True, 'message': 'İş emri güncellendi'})
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Invalid request'})

# Admin kayıtları
admin.site.register(IsEmri, IsEmriAdmin)
admin.site.register(UretimPlanlama, UretimPlanlamaAdmin)