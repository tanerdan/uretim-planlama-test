import React from 'react';
import { Row, Col, Card, Statistic, Typography, List, Progress, Button, Space, Table, Alert } from 'antd';
import { 
  ShoppingCartOutlined, 
  UserOutlined, 
  DollarOutlined, 
  RiseOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  EyeOutlined,
  BarChartOutlined,
  StopOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  MinusCircleOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { salesService } from '../../services/salesService';
import dayjs from 'dayjs';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup
} from "react-simple-maps";

const { Title } = Typography;

const ModuleHeader = styled.div`
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  color: white;
  padding: 32px 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 12px 12px;
  
  .dark-theme & {
    background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
  }
  
  .module-title {
    color: white;
    margin-bottom: 8px;
  }
  
  .module-desc {
    color: rgba(255,255,255,0.8);
    margin: 0;
  }
`;

const ActionCard = styled(Card)`
  .ant-card-body {
    padding: 16px;
    text-align: center;
  }
  
  &:hover {
    box-shadow: 0 4px 12px rgba(82, 196, 26, 0.15);
    transform: translateY(-2px);
    transition: all 0.3s ease;
  }
`;

const SalesDashboard: React.FC = () => {
  const navigate = useNavigate();
  
  // Gerçek API verilerini çek
  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['dashboard-orders'],
    queryFn: () => salesService.getOrders({ limit: 1000 }) // Tüm siparişleri al
  });

  const { data: customersData, isLoading: customersLoading } = useQuery({
    queryKey: ['dashboard-customers'],
    queryFn: () => salesService.getActiveCustomers()
  });

  const { data: salesStats, isLoading: statsLoading } = useQuery({
    queryKey: ['sales-stats'],
    queryFn: () => salesService.getSalesStats()
  });

  const orders = ordersData?.results || [];
  const customers = customersData || [];

  // İptal edilmeyen siparişler
  const activeOrders = orders.filter(order => order.durum !== 'iptal');

  // Sipariş durum istatistikleri (iptal edilmeyenler)
  const orderStatusStats = {
    beklemede: activeOrders.filter(o => o.durum === 'beklemede').length,
    malzeme_planlandi: activeOrders.filter(o => o.durum === 'malzeme_planlandi').length,
    is_emirleri_olusturuldu: activeOrders.filter(o => o.durum === 'is_emirleri_olusturuldu').length,
    uretimde: activeOrders.filter(o => o.durum === 'uretimde').length,
    tamamlandi: activeOrders.filter(o => o.durum === 'tamamlandi').length,
    iptal: orders.filter(o => o.durum === 'iptal').length, // İptal sayısı için tüm siparişler
  };
  
  // Yılbaşından bu yana veriler
  const yearStart = dayjs().startOf('year');
  const yearToDateOrders = activeOrders.filter(order => 
    dayjs(order.tarih).isAfter(yearStart)
  );
  const yearToDateRevenue = yearToDateOrders.reduce((sum, order) => 
    sum + (parseFloat(order.toplam_tutar) || 0), 0
  );

  // Bu ay veriler
  const thisMonthStart = dayjs().startOf('month');
  const thisMonthOrders = activeOrders.filter(order => 
    dayjs(order.tarih).isAfter(thisMonthStart)
  );
  const thisMonthRevenue = thisMonthOrders.reduce((sum, order) => 
    sum + (parseFloat(order.toplam_tutar) || 0), 0
  );

  // Helper function for number formatting with thousands separator
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Ana istatistikler
  const mainStats = [
    { 
      title: 'Toplam Siparişler', 
      value: formatNumber(activeOrders.length), 
      prefix: <ShoppingCartOutlined />, 
      color: '#1890ff' 
    },
    { 
      title: 'Aktif Müşteriler', 
      value: formatNumber(customers.length), 
      prefix: <UserOutlined />, 
      color: '#52c41a' 
    },
    { 
      title: 'Alınan Siparişler (Aylık)', 
      value: `$${formatNumber(Math.round(thisMonthRevenue))}`, 
      prefix: <DollarOutlined />, 
      color: '#722ed1' 
    },
    { 
      title: 'Alınan Siparişler (Yıllık)', 
      value: `$${formatNumber(Math.round(yearToDateRevenue))}`, 
      prefix: <RiseOutlined />, 
      color: '#13c2c2' 
    },
  ];

  // Son siparişler (son 5 sipariş - iptal edilmeyenler)
  const recentOrders = activeOrders
    .sort((a, b) => dayjs(b.olusturulma_tarihi).unix() - dayjs(a.olusturulma_tarihi).unix())
    .slice(0, 5)
    .map(order => ({
      id: order.siparis_no,
      orderId: order.id,
      customer: order.musteri_adi || `Müşteri ID: ${order.musteri}`,
      amount: `$${formatNumber(parseFloat(order.toplam_tutar || '0'))}`,
      status: order.durum,
      progress: getOrderProgress(order.durum),
      date: dayjs(order.olusturulma_tarihi).format('DD.MM.YYYY')
    }));

  // Teslim tarihi geçen siparişler (iptal edilmeyenler)
  const overdueOrders = activeOrders.filter(order => {
    if (!order.kalemler || order.durum === 'tamamlandi') return false;
    return order.kalemler.some(kalem => 
      dayjs(kalem.teslim_tarihi).isBefore(dayjs(), 'day')
    );
  }).slice(0, 5);

  // Sipariş durum dağılımı (Pie chart için)
  const statusDistribution = [
    { name: 'Beklemede', value: orderStatusStats.beklemede, color: '#1890ff' },
    { name: 'Malzeme Planlandı', value: orderStatusStats.malzeme_planlandi, color: '#fa8c16' },
    { name: 'İş Emirleri Oluşturuldu', value: orderStatusStats.is_emirleri_olusturuldu, color: '#722ed1' },
    { name: 'Üretimde', value: orderStatusStats.uretimde, color: '#52c41a' },
    { name: 'Tamamlandı', value: orderStatusStats.tamamlandi, color: '#13c2c2' },
    { name: 'İptal', value: orderStatusStats.iptal, color: '#ff4d4f' },
  ].filter(item => item.value > 0);

  // Aylık satış trendi (son 12 ay - iptal edilmeyenler)
  const getMonthlySales = () => {
    const months = [];
    for (let i = 11; i >= 0; i--) {
      const monthStart = dayjs().subtract(i, 'month').startOf('month');
      const monthEnd = dayjs().subtract(i, 'month').endOf('month');
      
      const monthOrders = activeOrders.filter(order => {
        const orderDate = dayjs(order.tarih);
        return orderDate.isAfter(monthStart) && orderDate.isBefore(monthEnd);
      });

      months.push({
        month: monthStart.format('MMM YY'),
        siparisler: monthOrders.length,
        ciro: monthOrders.reduce((sum, order) => sum + (parseFloat(order.toplam_tutar) || 0), 0)
      });
    }
    return months;
  };

  const monthlySales = getMonthlySales();

  // Ülkelere göre sipariş dağılımı
  const getCountryDistribution = () => {
    const countryMap: { [key: string]: { count: number; total: number; coords?: [number, number] } } = {};
    
    // Ülke koordinatları (başkent koordinatları)
    const countryCoords: { [key: string]: [number, number] } = {
      // Avrupa
      'TR': [35.2433, 38.9637], // Türkiye
      'DE': [13.4050, 52.5200], // Almanya  
      'FR': [2.2137, 46.2276], // Fransa
      'GB': [-3.4360, 55.3781], // İngiltere
      'IT': [12.5674, 41.8719], // İtalya
      'ES': [-3.7492, 40.4637], // İspanya
      'NL': [5.2913, 52.1326], // Hollanda
      'BE': [4.4699, 50.5039], // Belçika
      'CH': [8.2275, 46.8182], // İsviçre
      'AT': [16.3738, 48.2082], // Avusturya
      'SE': [18.0686, 59.3293], // İsveç
      'NO': [10.7522, 59.9139], // Norveç
      'DK': [12.5683, 55.6761], // Danimarka
      'FI': [24.9384, 60.1699], // Finlandiya
      'PL': [19.1451, 51.9194], // Polonya
      'CZ': [14.4378, 50.0755], // Çekya
      'HU': [19.5033, 47.1625], // Macaristan
      'RO': [24.9668, 45.9432], // Romanya
      'BG': [25.4858, 42.7339], // Bulgaristan
      'GR': [21.8243, 39.0742], // Yunanistan
      'PT': [-8.2245, 39.3999], // Portekiz
      'IE': [-8.2439, 53.4129], // İrlanda
      'SK': [19.6990, 48.6690], // Slovakya
      'SI': [14.9955, 46.1512], // Slovenya
      'HR': [15.2000, 45.1000], // Hırvatistan
      'RS': [21.0059, 44.0165], // Sırbistan
      'BA': [17.6791, 43.9159], // Bosna Hersek
      'MK': [21.7453, 41.6086], // Kuzey Makedonya
      'AL': [20.1683, 41.1533], // Arnavutluk
      'ME': [19.3744, 42.7087], // Karadağ
      'MD': [28.8497, 47.0105], // Moldova
      'UA': [31.1656, 48.3794], // Ukrayna
      'BY': [27.9534, 53.7098], // Belarus
      'LT': [23.8813, 55.1694], // Litvanya
      'LV': [24.6032, 56.8796], // Letonya
      'EE': [25.0136, 58.5953], // Estonya
      'IS': [-19.0208, 64.9631], // İzlanda
      'MT': [14.3754, 35.9375], // Malta
      'CY': [33.4299, 35.1264], // Kıbrıs
      'LU': [6.1296, 49.8153], // Lüksemburg
      // Amerika
      'US': [-95.7129, 37.0902], // ABD
      'CA': [-106.3468, 56.1304], // Kanada
      'MX': [-102.5528, 23.6345], // Meksika
      'BR': [-51.9253, -14.2350], // Brezilya
      'AR': [-63.6167, -38.4161], // Arjantin
      'CL': [-71.5430, -35.6751], // Şili
      'CO': [-74.2973, 4.5709], // Kolombiya
      'PE': [-75.0152, -9.1900], // Peru
      'VE': [-66.5897, 6.4238], // Venezuela
      'EC': [-78.1834, -1.8312], // Ekvador
      'UY': [-55.7658, -32.5228], // Uruguay
      'PY': [-58.4438, -23.4425], // Paraguay
      'BO': [-63.5887, -16.2902], // Bolivya
      // Asya
      'RU': [105.3188, 61.5240], // Rusya
      'CN': [104.1954, 35.8617], // Çin
      'JP': [138.2529, 36.2048], // Japonya
      'KR': [127.7669, 35.9078], // Güney Kore
      'IN': [78.9629, 20.5937], // Hindistan
      'ID': [113.9213, -0.7893], // Endonezya
      'TH': [100.9925, 15.8700], // Tayland
      'MY': [101.9758, 4.2105], // Malezya
      'SG': [103.8198, 1.3521], // Singapur
      'PH': [121.7740, 12.8797], // Filipinler
      'VN': [108.2772, 14.0583], // Vietnam
      'KZ': [66.9237, 48.0196], // Kazakistan
      'UZ': [64.5853, 41.3775], // Özbekistan
      'TM': [59.5563, 38.9697], // Türkmenistan
      'KG': [74.7661, 41.2044], // Kırgızistan
      'TJ': [71.2761, 38.8610], // Tacikistan
      'AF': [67.7090, 33.9391], // Afganistan
      'PK': [69.3451, 30.3753], // Pakistan
      'BD': [90.3563, 23.6850], // Bangladeş
      'LK': [80.7718, 7.8731], // Sri Lanka
      'MM': [95.9560, 21.9162], // Myanmar
      'KH': [104.9910, 12.5657], // Kamboçya
      'LA': [102.4955, 19.8563], // Laos
      'MN': [103.8467, 46.8625], // Moğolistan
      // Orta Doğu
      'SA': [45.0792, 23.8859], // Suudi Arabistan
      'AE': [53.8478, 23.4241], // BAE
      'QA': [51.1839, 25.3548], // Katar
      'KW': [47.4818, 29.3117], // Kuveyt
      'BH': [50.6344, 26.0667], // Bahreyn
      'OM': [55.9754, 21.4735], // Umman
      'YE': [48.5164, 15.5527], // Yemen
      'SY': [38.9968, 34.8021], // Suriye
      'LB': [35.8623, 33.8547], // Lübnan
      'JO': [36.2384, 30.5852], // Ürdün
      'IL': [34.8516, 31.0461], // İsrail
      'PS': [35.2332, 31.9522], // Filistin
      'IQ': [43.6793, 33.2232], // Irak
      'IR': [53.6880, 32.4279], // İran
      'GE': [43.3569, 42.3154], // Gürcistan
      'AM': [45.0382, 40.0691], // Ermenistan
      'AZ': [47.5769, 40.1431], // Azerbaycan
      // Afrika
      'EG': [30.8025, 26.8206], // Mısır
      'ZA': [22.9375, -30.5595], // Güney Afrika
      'NG': [8.6753, 9.0820], // Nijerya
      'KE': [37.9062, -0.0236], // Kenya
      'ET': [40.4897, 9.1450], // Etiyopya
      'GH': [-1.0232, 7.9465], // Gana
      'MA': [-7.0926, 31.7917], // Fas
      'DZ': [1.6596, 28.0339], // Cezayir
      'TN': [9.5375, 33.8869], // Tunus
      'LY': [17.2283, 26.3351], // Libya
      'SD': [30.2176, 12.8628], // Sudan
      // Okyanusya
      'AU': [133.7751, -25.2744], // Avustralya
      'NZ': [174.8860, -40.9006], // Yeni Zelanda
      'FJ': [179.4144, -16.5780], // Fiji
      'PG': [143.9555, -6.3150], // Papua Yeni Gine
    };
    
    activeOrders.forEach(order => {
      // Eğer kalemler varsa, her kalem için ayrı ayrı hesapla
      if (order.kalemler && order.kalemler.length > 0) {
        order.kalemler.forEach(kalem => {
          const country = kalem.son_kullanici_ulke || order.son_kullanici_ulke || order.musteri_ulke || 'TR';
          if (!countryMap[country]) {
            countryMap[country] = { 
              count: 0, 
              total: 0, 
              coords: countryCoords[country] || [35.2433, 38.9637] 
            };
          }
          countryMap[country].count += 1; // Her kalem bir sipariş olarak sayılır
          countryMap[country].total += parseFloat(kalem.toplam_tutar || '0'); // Kalem tutarını kullan
        });
      } else {
        // Kalem yoksa sipariş seviyesinde hesapla (fallback)
        const country = order.son_kullanici_ulke || order.musteri_ulke || 'TR';
        if (!countryMap[country]) {
          countryMap[country] = { 
            count: 0, 
            total: 0, 
            coords: countryCoords[country] || [35.2433, 38.9637] 
          };
        }
        countryMap[country].count += 1;
        countryMap[country].total += parseFloat(order.toplam_tutar || '0');
      }
    });

    // Test için sahte veri ekle eğer gerçek veri yoksa
    if (Object.keys(countryMap).length === 0) {
      countryMap['TR'] = { count: 5, total: 250000, coords: [35.2433, 38.9637] };
      countryMap['DE'] = { count: 3, total: 180000, coords: [13.4050, 52.5200] };
      countryMap['US'] = { count: 2, total: 120000, coords: [-95.7129, 37.0902] };
    }

    return Object.entries(countryMap)
      .map(([country, data]) => ({
        country,
        count: data.count,
        total: data.total,
        coords: data.coords,
        // Marker boyutu için normalize et (min: 5, max: 25)
        markerSize: Math.max(5, Math.min(25, (data.total / 50000) * 10))
      }))
      .sort((a, b) => b.total - a.total);
  };

  const countryDistribution = getCountryDistribution();

  // Helper function for order progress
  function getOrderProgress(status: string): number {
    switch (status) {
      case 'beklemede': return 10;
      case 'malzeme_planlandi': return 25;
      case 'is_emirleri_olusturuldu': return 50;
      case 'uretimde': return 75;
      case 'tamamlandi': return 100;
      case 'iptal': return 0;
      default: return 0;
    }
  }

  // Status labels
  const statusLabels = {
    'beklemede': 'Beklemede',
    'malzeme_planlandi': 'Malzeme Planlandı',
    'is_emirleri_olusturuldu': 'İş Emirleri Oluşturuldu',
    'uretimde': 'Üretimde',
    'tamamlandi': 'Tamamlandı',
    'iptal': 'İptal'
  };

  const quickActions = [
    { title: 'Yeni Sipariş', icon: <PlusOutlined />, action: () => navigate('/sales/orders/new'), color: '#52c41a' },
    { title: 'Siparişleri Görüntüle', icon: <EyeOutlined />, action: () => navigate('/sales/orders'), color: '#1890ff' },
    { title: 'Sipariş Değişiklikleri', icon: <EditOutlined />, action: () => navigate('/sales/orders/changes'), color: '#722ed1' },
    { title: 'Sipariş İptali', icon: <StopOutlined />, action: () => navigate('/sales/orders/cancel'), color: '#ff4d4f' },
  ];

  const isLoading = ordersLoading || customersLoading || statsLoading;

  return (
    <div>
      <ModuleHeader>
        <Title level={2} className="module-title">
          <ShoppingCartOutlined /> Satış Modülü
        </Title>
        <p className="module-desc">
          Müşteri siparişleri, teklif yönetimi ve satış performansı takibi
        </p>
      </ModuleHeader>

      {/* Teslim tarihi geçen siparişler uyarısı */}
      {overdueOrders.length > 0 && (
        <Alert
          message={`${overdueOrders.length} siparişin teslim tarihi geçmiş!`}
          description={
            <div>
              Teslim tarihi geçen siparişler: {overdueOrders.map(order => order.siparis_no).join(', ')}
            </div>
          }
          type="warning"
          showIcon
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: '24px' }}
          action={
            <Button size="small" onClick={() => navigate('/sales/orders')}>
              Detay Görüntüle
            </Button>
          }
        />
      )}

      {/* İstatistikler */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {mainStats.map((stat, index) => (
          <Col xs={12} sm={6} key={index}>
            <Card loading={isLoading}>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={React.cloneElement(stat.prefix, { style: { color: stat.color } })}
                valueStyle={{ color: stat.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* Hızlı İşlemler */}
      <Card title="Hızlı İşlemler" style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          {quickActions.map((action, index) => (
            <Col xs={12} sm={6} key={index}>
              <ActionCard hoverable onClick={action.action}>
                <div style={{ color: action.color, fontSize: '32px', marginBottom: '12px' }}>
                  {action.icon}
                </div>
                <div style={{ fontWeight: 'bold' }}>{action.title}</div>
              </ActionCard>
            </Col>
          ))}
        </Row>
      </Card>

      <Row gutter={[16, 16]}>
        {/* Sipariş Durum Dağılımı */}
        <Col xs={24} lg={12}>
          <Card title="Sipariş Durum Dağılımı" size="small" loading={isLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Aylık Satış Trendi */}
        <Col xs={24} lg={12}>
          <Card title="Son 12 Ay Satış Performansı" size="small" loading={isLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlySales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value, name) => {
                  if (name === 'ciro') {
                    return [`$${formatNumber(Number(value))}`, 'Alınan Siparişler (USD)'];
                  }
                  return [formatNumber(Number(value)), 'Sipariş Sayısı'];
                }} />
                <Line type="monotone" dataKey="siparisler" stroke="#1890ff" name="siparisler" />
                <Line type="monotone" dataKey="ciro" stroke="#52c41a" name="ciro" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Son Siparişler */}
        <Col xs={24} lg={12}>
          <Card 
            title="Son Siparişler" 
            size="small" 
            loading={isLoading}
            extra={<Button type="link" onClick={() => navigate('/sales/orders')}>Tümünü Gör</Button>}
          >
            <List
              itemLayout="horizontal"
              dataSource={recentOrders}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Button 
                        type="link" 
                        onClick={() => navigate(`/sales/orders/${item.orderId}`)}
                        style={{ padding: 0, fontWeight: 'bold' }}
                      >
                        {item.id}
                      </Button>
                    }
                    description={`${item.customer} • ${item.date}`}
                  />
                  <div style={{ textAlign: 'right', minWidth: '120px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{item.amount}</div>
                    <Progress 
                      percent={item.progress} 
                      size="small"
                      strokeColor={item.progress === 100 ? '#52c41a' : item.progress === 0 ? '#ff4d4f' : '#1890ff'}
                    />
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {statusLabels[item.status as keyof typeof statusLabels]}
                    </div>
                  </div>
                </List.Item>
              )}
              locale={{ emptyText: 'Henüz sipariş bulunmuyor' }}
            />
          </Card>
        </Col>

        {/* Teslim Tarihi Geçen Siparişler */}
        <Col xs={24} lg={12}>
          <Card 
            title="Teslim Tarihi Geçen Siparişler" 
            size="small"
            loading={isLoading}
            extra={
              overdueOrders.length > 0 ? (
                <Button 
                  type="link" 
                  danger
                  onClick={() => navigate('/sales/orders')}
                >
                  Acil Müdahale
                </Button>
              ) : null
            }
          >
            {overdueOrders.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px', color: '#52c41a' }}>
                <CheckCircleOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
                <div>Teslim tarihi geçen sipariş bulunmuyor</div>
              </div>
            ) : (
              <List
                itemLayout="horizontal"
                dataSource={overdueOrders.slice(0, 5)}
                renderItem={item => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <ExclamationCircleOutlined style={{ color: '#ff4d4f', fontSize: '16px' }} />
                      }
                      title={
                        <Button 
                          type="link" 
                          onClick={() => navigate(`/sales/orders/${item.id}`)}
                          style={{ padding: 0, fontWeight: 'bold' }}
                        >
                          {item.siparis_no}
                        </Button>
                      }
                      description={item.musteri_adi || `Müşteri ID: ${item.musteri}`}
                    />
                    <div style={{ color: '#ff4d4f', fontSize: '12px' }}>
                      <CalendarOutlined /> {dayjs(item.kalemler?.[0]?.teslim_tarihi).format('DD.MM.YYYY')}
                    </div>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        {/* Müşteri İstatistikleri */}
        <Col xs={24} lg={12}>
          <Card title="Müşteri İstatistikleri" size="small" loading={isLoading}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic 
                  title="Aktif Müşteriler" 
                  value={formatNumber(customers.length)} 
                  prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Sipariş Veren" 
                  value={formatNumber(new Set(activeOrders.map(o => o.musteri)).size)} 
                  prefix={<UserOutlined style={{ color: '#1890ff' }} />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <div style={{ marginBottom: '8px', fontSize: '14px', color: '#666' }}>
                Müşteri Başına Ortalama Sipariş Değeri
              </div>
              <Statistic
                value={activeOrders.length > 0 ? 
                  formatNumber(Math.round(activeOrders.reduce((sum, order) => sum + (parseFloat(order.toplam_tutar) || 0), 0) / 
                   new Set(activeOrders.map(o => o.musteri)).size))
                  : 0
                }
                prefix="$"
                precision={0}
                valueStyle={{ fontSize: '18px', color: '#722ed1' }}
              />
            </div>
          </Card>
        </Col>

        {/* Dünya Haritası - Sipariş Dağılımı */}
        <Col xs={24} lg={12}>
          <Card title="Sipariş Dağılımı (Ülkelere Göre)" size="small" loading={isLoading}>
            <div style={{ width: '100%', height: '300px', position: 'relative' }}>
              {countryDistribution.length === 0 ? (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '100%',
                  color: '#999'
                }}>
                  Sipariş verisi yükleniyor veya sipariş bulunmuyor...
                </div>
              ) : (
                <ComposableMap
                  projection="geoMercator"
                  projectionConfig={{
                    scale: 120,
                    center: [20, 50]
                  }}
                  width={400}
                  height={280}
                  style={{ width: '100%', height: '100%' }}
                >
                  <ZoomableGroup>
                    <Geographies 
                      geography="https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson"
                    >
                      {({ geographies }) => 
                        geographies?.map((geo) => (
                          <Geography
                            key={geo.rsmKey}
                            geography={geo}
                            fill="#E5E7EB"
                            stroke="#D1D5DB"
                            strokeWidth={0.5}
                            style={{
                              default: { outline: "none" },
                              hover: { outline: "none", fill: "#F3F4F6" },
                              pressed: { outline: "none" }
                            }}
                          />
                        )) || []
                      }
                    </Geographies>
                    {countryDistribution.map(({ country, total, count, coords, markerSize }) => (
                      coords && (
                        <Marker key={country} coordinates={coords}>
                          <circle
                            r={markerSize}
                            fill="#1890ff"
                            fillOpacity={0.7}
                            stroke="#fff"
                            strokeWidth={2}
                          />
                          <title>
                            {country}: {formatNumber(count)} sipariş, ${formatNumber(Math.round(total))}
                          </title>
                        </Marker>
                      )
                    ))}
                  </ZoomableGroup>
                </ComposableMap>
              )}
            </div>
            <div style={{ 
              fontSize: '10px', 
              color: '#999', 
              textAlign: 'center', 
              marginTop: '4px',
              fontStyle: 'italic'
            }}>
              💡 Haritayı zoom yapmak için tekerleği kullanın, sürükleyerek hareket ettirin
            </div>
            <div style={{ marginTop: '12px' }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                En Büyük Pazarlar:
              </div>
              {countryDistribution.slice(0, 3).map(({ country, count, total }) => (
                <div key={country} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  fontSize: '12px',
                  marginBottom: '4px'
                }}>
                  <span>{country}:</span>
                  <span>{formatNumber(count)} sipariş, ${formatNumber(Math.round(total))}</span>
                </div>
              ))}
            </div>
          </Card>
        </Col>

        {/* Bu Ay vs Geçen Ay */}
        <Col xs={24} lg={12}>
          <Card title="Bu Ay vs Geçen Ay" size="small" loading={isLoading}>
            {(() => {
              const thisMonth = dayjs().startOf('month');
              const lastMonth = dayjs().subtract(1, 'month').startOf('month');
              const thisMonthEnd = dayjs().endOf('month');
              const lastMonthEnd = dayjs().subtract(1, 'month').endOf('month');
              
              const thisMonthOrders = activeOrders.filter(order => 
                dayjs(order.tarih).isAfter(thisMonth) && dayjs(order.tarih).isBefore(thisMonthEnd)
              );
              const lastMonthOrders = activeOrders.filter(order => 
                dayjs(order.tarih).isAfter(lastMonth) && dayjs(order.tarih).isBefore(lastMonthEnd)
              );
              
              const thisMonthRevenue = thisMonthOrders.reduce((sum, order) => sum + (parseFloat(order.toplam_tutar) || 0), 0);
              const lastMonthRevenue = lastMonthOrders.reduce((sum, order) => sum + (parseFloat(order.toplam_tutar) || 0), 0);
              
              const revenueChange = lastMonthRevenue > 0 ? ((thisMonthRevenue - lastMonthRevenue) / lastMonthRevenue * 100) : 0;
              const orderChange = lastMonthOrders.length > 0 ? ((thisMonthOrders.length - lastMonthOrders.length) / lastMonthOrders.length * 100) : 0;
              
              return (
                <>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic 
                        title="Bu Ay Sipariş" 
                        value={formatNumber(thisMonthOrders.length)}
                        valueStyle={{ color: orderChange >= 0 ? '#52c41a' : '#ff4d4f' }}
                        prefix={orderChange >= 0 ? <RiseOutlined /> : <MinusCircleOutlined />}
                        suffix={`(${orderChange >= 0 ? '+' : ''}${orderChange.toFixed(1)}%)`}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic 
                        title="Bu Ay Alınan Siparişler" 
                        value={formatNumber(Math.round(thisMonthRevenue))}
                        precision={0}
                        prefix="$"
                        valueStyle={{ color: revenueChange >= 0 ? '#52c41a' : '#ff4d4f' }}
                        suffix={`(${revenueChange >= 0 ? '+' : ''}${revenueChange.toFixed(1)}%)`}
                      />
                    </Col>
                  </Row>
                  <div style={{ marginTop: '16px', fontSize: '12px', color: '#666' }}>
                    Geçen Ay: {formatNumber(lastMonthOrders.length)} sipariş, ${formatNumber(Math.round(lastMonthRevenue))} alınan siparişler
                  </div>
                </>
              );
            })()}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SalesDashboard;