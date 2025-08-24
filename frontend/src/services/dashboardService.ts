import api from './api';
import { ApiResponse, Siparis, Musteri, Urun, DashboardStats } from '../types';

export const dashboardService = {
  // Get dashboard statistics
  getStats: async (): Promise<DashboardStats> => {
    try {
      // Get data from multiple endpoints
      const [siparisRes, musteriRes, urunRes] = await Promise.all([
        api.get<ApiResponse<Siparis>>('/siparisler/'),
        api.get<ApiResponse<Musteri>>('/musteriler/'),
        api.get<ApiResponse<Urun>>('/urunler/'),
      ]);

      const siparisler = siparisRes.data.results;
      
      // Calculate statistics
      const stats: DashboardStats = {
        aktif_siparisler: siparisler.filter(s => 
          ['beklemede', 'malzeme_planlandi', 'is_emirleri_olusturuldu', 'uretimde'].includes(s.durum)
        ).length,
        uretimde: siparisler.filter(s => s.durum === 'uretimde').length,
        tamamlanan: siparisler.filter(s => s.durum === 'tamamlandi').length,
        bekleyen: siparisler.filter(s => s.durum === 'beklemede').length,
        toplam_musteri: musteriRes.data.results.length,
        toplam_urun: urunRes.data.results.length,
      };

      return stats;
    } catch (error) {
      console.error('Dashboard stats error:', error);
      throw error;
    }
  },

  // Get recent orders
  getRecentOrders: async (limit: number = 10): Promise<Siparis[]> => {
    try {
      const response = await api.get<ApiResponse<Siparis>>(`/siparisler/?limit=${limit}&ordering=-olusturulma_tarihi`);
      return response.data.results;
    } catch (error) {
      console.error('Recent orders error:', error);
      throw error;
    }
  },

  // Get order status distribution for pie chart
  getOrderStatusDistribution: async () => {
    try {
      const response = await api.get<ApiResponse<Siparis>>('/siparisler/');
      const siparisler = response.data.results;
      
      const statusCounts = siparisler.reduce((acc, siparis) => {
        acc[siparis.durum] = (acc[siparis.durum] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      return [
        { name: 'Tamamlanan', value: statusCounts.tamamlandi || 0, color: '#52c41a' },
        { name: 'Üretimde', value: statusCounts.uretimde || 0, color: '#1890ff' },
        { name: 'Bekleyen', value: statusCounts.beklemede || 0, color: '#faad14' },
        { name: 'Planlanan', value: (statusCounts.malzeme_planlandi || 0) + (statusCounts.is_emirleri_olusturuldu || 0), color: '#722ed1' },
      ];
    } catch (error) {
      console.error('Status distribution error:', error);
      throw error;
    }
  },

  // Get monthly performance data
  getMonthlyPerformance: async () => {
    try {
      const response = await api.get<ApiResponse<Siparis>>('/siparisler/');
      const siparisler = response.data.results;
      
      // Group by month (simplified for now - you might want to use date-fns)
      const monthlyData = Array.from({ length: 6 }, (_, i) => {
        const month = new Date();
        month.setMonth(month.getMonth() - i);
        const monthName = month.toLocaleDateString('tr-TR', { month: 'long' });
        
        const monthOrders = siparisler.filter(s => {
          const orderMonth = new Date(s.tarih).getMonth();
          const targetMonth = month.getMonth();
          return orderMonth === targetMonth;
        });

        return {
          name: monthName,
          siparisler: monthOrders.length,
          uretim: monthOrders.filter(s => ['uretimde', 'tamamlandi'].includes(s.durum)).length,
        };
      }).reverse();

      return monthlyData;
    } catch (error) {
      console.error('Monthly performance error:', error);
      throw error;
    }
  },
};