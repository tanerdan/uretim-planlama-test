// API response types based on Django models

export interface Ulke {
  kod: string;
  ad: string;
}

export interface Musteri {
  id: number;
  ad: string;
  kod: string;
  telefon: string;
  email: string;
  adres: string;
  ulke: string;
  notlar: string;
  aktif: boolean;
  olusturulma_tarihi: string;
  guncellenme_tarihi: string;
}

export interface Urun {
  id: number;
  ad: string;
  kod: string;
  kategori: 'hammadde' | 'ara_urun' | 'bitmis_urun';
  birim: string;
  stok_miktari: number;
  minimum_stok: number;
  stok_durumu?: string;
  olusturulma_tarihi: string;
  guncellenme_tarihi: string;
}

export interface SiparisDosya {
  id: number;
  dosya: string;
  aciklama: string;
  yuklenme_tarihi: string;
}

export interface Siparis {
  id: number;
  siparis_no: string;
  musteri: number;
  tarih: string;
  durum: 'beklemede' | 'malzeme_planlandi' | 'is_emirleri_olusturuldu' | 'uretimde' | 'tamamlandi' | 'iptal';
  musteri_ulke: string;
  son_kullanici_ulke: string;
  toplam_tutar: number;
  notlar: string;
  olusturulma_tarihi: string;
  guncellenme_tarihi: string;
  musteri_adi?: string;
  dosya?: string;
  kalemler?: SiparisKalem[];
  dosyalar?: SiparisDosya[];
}

// API submission için ayrı tip - kalemler JSON string olarak gönderiliyor
export interface SiparisApiPayload {
  siparis_no: string;
  musteri: number;
  tarih: string;
  durum?: 'beklemede' | 'malzeme_planlandi' | 'is_emirleri_olusturuldu' | 'uretimde' | 'tamamlandi' | 'iptal';
  musteri_ulke: string;
  son_kullanici_ulke: string;
  notlar: string;
  kalemler: string; // JSON string
}

export interface SiparisKalem {
  id: number;
  siparis: number;
  urun: number;
  urun_adi?: string;
  miktar: number;
  birim_fiyat: number;
  doviz: string;
  kur: number;
  birim_fiyat_usd: number;
  teslim_tarihi: string;
  son_kullanici_ulke: string;
  toplam_tutar: number;
  olusturulma_tarihi: string;
  notlar?: string;
  urun_detail?: Urun;
  siparis_detail?: Siparis;
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DashboardStats {
  aktif_siparisler: number;
  uretimde: number;
  tamamlanan: number;
  bekleyen: number;
  toplam_musteri: number;
  toplam_urun: number;
}