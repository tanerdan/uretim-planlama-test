// Django admin jQuery kullanım
(function() {
    'use strict';
    
    // Django'nun jQuery'sini kullan
    var $ = django.jQuery;
    
    $(document).ready(function() {
        
        // Toplam tutarı hesapla
        function calculateTotal() {
            var gelenMiktar = parseFloat($('#id_gelen_miktar').val()) || 0;
            var birimFiyat = parseFloat($('#id_birim_fiyat').val()) || 0;
            var toplam = gelenMiktar * birimFiyat;
            
            $('#id_toplam_tutar').val(toplam.toFixed(4));
        }
        
        // Malzeme kalemi seçildiğinde birim bilgisini güncelle
        function updateBirimInfo() {
            var kalemiSelect = $('#id_satinalma_kalemi');
            var gelenMiktarContainer = $('#id_gelen_miktar').closest('.form-row');
            
            if (kalemiSelect.val()) {
                var selectedText = kalemiSelect.find('option:selected').text();
                console.log('Seçilen kalem:', selectedText);
                
                // "Malzeme Adı - 100 birim (SA-123)" formatından birim çıkar
                // Önce " - " ile ayır, sonra birim kısmını bul
                var parts = selectedText.split(' - ');
                if (parts.length > 1) {
                    var miktarBirimKismi = parts[1]; // "100 kg (SA-123)" kısmı
                    var birimMatch = miktarBirimKismi.match(/[\d.]+\s+(\w+)/);
                    if (birimMatch) {
                        var birim = birimMatch[1];
                        console.log('Bulunan birim:', birim);
                        
                        // Mevcut birim bilgisini temizle
                        gelenMiktarContainer.find('.birim-info').remove();
                        
                        // Yeni birim bilgisini ekle
                        gelenMiktarContainer.append('<p class="help birim-info" style="color: #666; font-size: 11px; margin-top: 2px;">Birim: <strong>' + birim + '</strong></p>');
                        
                        // Label'ı da güncelle
                        var gelenMiktarLabel = $('label[for="id_gelen_miktar"]');
                        var originalLabel = gelenMiktarLabel.text().replace(/\s*\([^)]*\)$/, ''); // Eski birim bilgisini temizle
                        gelenMiktarLabel.text(originalLabel + ' (' + birim + ')');
                    }
                }
            } else {
                // Seçim yoksa birim bilgisini temizle
                gelenMiktarContainer.find('.birim-info').remove();
                var gelenMiktarLabel = $('label[for="id_gelen_miktar"]');
                gelenMiktarLabel.text('Gelen Miktar');
            }
        }
        
        // Event listener'ları ekle
        $('#id_satinalma_kalemi').change(function() {
            updateBirimInfo();
            calculateTotal();
        });
        
        $('#id_gelen_miktar, #id_birim_fiyat').on('input change', calculateTotal);
        
        // Sayfa yüklendiğinde çalıştır
        updateBirimInfo();
        calculateTotal();
    });
    
})();