import api from './api';
import { ApiResponse, Siparis, Musteri, SiparisKalem, Urun, Ulke } from '../types';

export const salesService = {
  // Kur servisleri
  getExchangeRates: async (baseCurrency = 'USD'): Promise<any> => {
    try {
      const response = await api.get(`/exchange-rates/?base=${baseCurrency}`);
      return response.data;
    } catch (error) {
      console.error('Get exchange rates error:', error);
      throw error;
    }
  },

  convertCurrency: async (amount: number, fromCurrency: string, toCurrency: string): Promise<any> => {
    try {
      const response = await api.post('/convert-currency/', {
        amount,
        from_currency: fromCurrency,
        to_currency: toCurrency,
      });
      return response.data;
    } catch (error) {
      console.error('Convert currency error:', error);
      throw error;
    }
  },

  getCurrencies: async (): Promise<any> => {
    try {
      const response = await api.get('/currencies/');
      return response.data;
    } catch (error) {
      console.error('Get currencies error:', error);
      throw error;
    }
  },
  // Sipariş servisleri
  getOrders: async (params?: {
    page?: number;
    limit?: number;
    durum?: string;
    musteri?: number;
    search?: string;
  }): Promise<ApiResponse<Siparis>> => {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.limit) queryParams.append('page_size', params.limit.toString());
      if (params?.durum) queryParams.append('durum', params.durum);
      if (params?.musteri) queryParams.append('musteri', params.musteri.toString());
      if (params?.search) queryParams.append('search', params.search);

      const response = await api.get<ApiResponse<Siparis>>(`/siparisler/?${queryParams}`);
      return response.data;
    } catch (error) {
      console.error('Get orders error:', error);
      throw error;
    }
  },

  getOrderById: async (id: number): Promise<Siparis> => {
    try {
      const response = await api.get<Siparis>(`/siparisler/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Get order by id error:', error);
      throw error;
    }
  },

  createOrder: async (orderData: Partial<Siparis>): Promise<Siparis> => {
    try {
      const response = await api.post<Siparis>('/siparisler/', orderData);
      return response.data;
    } catch (error) {
      console.error('Create order error:', error);
      throw error;
    }
  },

  updateOrder: async (id: number, orderData: Partial<Siparis>): Promise<Siparis> => {
    try {
      const response = await api.put<Siparis>(`/siparisler/${id}/`, orderData);
      return response.data;
    } catch (error) {
      console.error('Update order error:', error);
      throw error;
    }
  },

  updateOrderStatus: async (id: number, status: string): Promise<Siparis> => {
    try {
      const response = await api.patch<Siparis>(`/siparisler/${id}/`, { durum: status });
      return response.data;
    } catch (error) {
      console.error('Update order status error:', error);
      throw error;
    }
  },

  // Sipariş kalemleri
  getOrderItems: async (orderId: number): Promise<SiparisKalem[]> => {
    try {
      const response = await api.get<SiparisKalem[]>(`/siparisler/${orderId}/kalemler/`);
      return response.data;
    } catch (error) {
      console.error('Get order items error:', error);
      throw error;
    }
  },

  // Müşteri servisleri
  getCustomers: async (params?: {
    page?: number;
    limit?: number;
    aktif?: boolean;
    search?: string;
  }): Promise<ApiResponse<Musteri>> => {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.limit) queryParams.append('page_size', params.limit.toString());
      if (params?.aktif !== undefined) queryParams.append('aktif', params.aktif.toString());
      if (params?.search) queryParams.append('search', params.search);

      const response = await api.get<ApiResponse<Musteri>>(`/musteriler/?${queryParams}`);
      return response.data;
    } catch (error) {
      console.error('Get customers error:', error);
      throw error;
    }
  },

  getCustomerById: async (id: number): Promise<Musteri> => {
    try {
      const response = await api.get<Musteri>(`/musteriler/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Get customer by id error:', error);
      throw error;
    }
  },

  createCustomer: async (customerData: Partial<Musteri>): Promise<Musteri> => {
    try {
      const response = await api.post<Musteri>('/musteriler/', customerData);
      return response.data;
    } catch (error) {
      console.error('Create customer error:', error);
      throw error;
    }
  },

  updateCustomer: async (id: number, customerData: Partial<Musteri>): Promise<Musteri> => {
    try {
      const response = await api.put<Musteri>(`/musteriler/${id}/`, customerData);
      return response.data;
    } catch (error) {
      console.error('Update customer error:', error);
      throw error;
    }
  },

  deleteCustomer: async (id: number): Promise<void> => {
    try {
      await api.delete(`/musteriler/${id}/`);
    } catch (error) {
      console.error('Delete customer error:', error);
      throw error;
    }
  },

  // Aktif müşteriler
  getActiveCustomers: async (): Promise<Musteri[]> => {
    try {
      const response = await api.get<Musteri[]>('/musteriler/aktif_musteriler/');
      return response.data;
    } catch (error) {
      console.error('Get active customers error:', error);
      throw error;
    }
  },

  // Ürün servisleri
  getProducts: async (params?: {
    page?: number;
    limit?: number;
    kategori?: string;
    search?: string;
  }): Promise<ApiResponse<Urun>> => {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.limit) queryParams.append('page_size', params.limit.toString());
      if (params?.kategori) queryParams.append('kategori', params.kategori);
      if (params?.search) queryParams.append('search', params.search);

      const response = await api.get<ApiResponse<Urun>>(`/urunler/?${queryParams}`);
      return response.data;
    } catch (error) {
      console.error('Get products error:', error);
      throw error;
    }
  },

  getProductById: async (id: number): Promise<Urun> => {
    try {
      const response = await api.get<Urun>(`/urunler/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Get product by id error:', error);
      throw error;
    }
  },

  // Satış istatistikleri
  getSalesStats: async (): Promise<{
    toplam_siparisler: number;
    aktif_musteriler: number;
    aylik_ciro: number;
    buyume_orani: number;
  }> => {
    try {
      // Gerçek API endpoint'i olmadığı için mock data döneriz
      // Gelecekte gerçek endpoint eklenebilir
      const [orders, customers] = await Promise.all([
        salesService.getOrders({ limit: 1000 }),
        salesService.getCustomers({ limit: 1000 })
      ]);

      return {
        toplam_siparisler: orders.count,
        aktif_musteriler: customers.results.filter(c => c.aktif).length,
        aylik_ciro: orders.results.reduce((sum, order) => sum + (order.toplam_tutar || 0), 0),
        buyume_orani: 15 // Mock değer
      };
    } catch (error) {
      console.error('Get sales stats error:', error);
      throw error;
    }
  },

  // Dosya yükleme
  uploadOrderFile: async (orderId: number, file: File, aciklama?: string): Promise<any> => {
    try {
      const formData = new FormData();
      formData.append('dosya', file);
      if (aciklama) formData.append('aciklama', aciklama);

      const response = await api.post(`/siparisler/${orderId}/dosya_ekle/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Upload order file error:', error);
      throw error;
    }
  },

  // Mikro Fly V17 Entegrasyonu
  syncCustomersFromMikroFly: async (): Promise<{
    synchronized_count: number;
    updated_count: number;
    new_count: number;
    message: string;
  }> => {
    try {
      const response = await api.post('/musteriler/mikro_fly_sync/', {});
      return response.data;
    } catch (error) {
      console.error('Mikro Fly sync error:', error);
      throw error;
    }
  },

  // Ürün senkronizasyonu
  syncProductsFromMikroFly: async (): Promise<{
    synchronized_count: number;
    updated_count: number;
    new_count: number;
    message: string;
  }> => {
    try {
      const response = await api.post('/urunler/mikro_fly_sync/', {});
      return response.data;
    } catch (error) {
      console.error('Mikro Fly product sync error:', error);
      throw error;
    }
  },

  // Senkronizasyon durumu
  getSyncStatus: async (): Promise<{
    last_sync: string | null;
    is_connected: boolean;
    mikro_fly_version: string;
    total_customers_in_mikro: number;
    total_customers_synced: number;
  }> => {
    try {
      const response = await api.get('/musteriler/sync_status/');
      return response.data;
    } catch (error) {
      console.error('Get sync status error:', error);
      throw error;
    }
  },

  // Ülke servisleri
  getCountries: async (): Promise<Ulke[]> => {
    try {
      const response = await api.get<Ulke[]>('/ulkeler/');
      return response.data;
    } catch (error) {
      console.error('Get countries error:', error);
      throw error;
    }
  },
};