import React from 'react';
import { Row, Col, Card, Statistic, Progress, Typography, List, Avatar, Spin, Alert } from 'antd';
import { 
  ShoppingCartOutlined, 
  BuildOutlined, 
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  InboxOutlined
} from '@ant-design/icons';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import styled from 'styled-components';
import { dashboardService } from '../services/dashboardService';

const { Title } = Typography;

const StyledCard = styled(Card)`
  .ant-card-head {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    
    .ant-card-head-title {
      color: white;
    }
  }
`;

// Status mapping for Turkish display
const statusDisplayMap: Record<string, string> = {
  'beklemede': 'Beklemede',
  'malzeme_planlandi': 'Malzeme Planlandı',
  'is_emirleri_olusturuldu': 'İş Emirleri Oluşturuldu',
  'uretimde': 'Üretimde',
  'tamamlandi': 'Tamamlandı'
};

const statusProgressMap: Record<string, number> = {
  'beklemede': 10,
  'malzeme_planlandi': 25,
  'is_emirleri_olusturuldu': 50,
  'uretimde': 75,
  'tamamlandi': 100
};

const Dashboard: React.FC = () => {
  // React Query hooks for data fetching
  const { 
    data: stats, 
    isLoading: statsLoading, 
    error: statsError 
  } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardService.getStats,
  });

  const { 
    data: recentOrders, 
    isLoading: ordersLoading,
    error: ordersError 
  } = useQuery({
    queryKey: ['recent-orders'],
    queryFn: () => dashboardService.getRecentOrders(5),
  });

  const { 
    data: statusDistribution, 
    isLoading: statusLoading 
  } = useQuery({
    queryKey: ['status-distribution'],
    queryFn: dashboardService.getOrderStatusDistribution,
  });

  const { 
    data: monthlyPerformance, 
    isLoading: monthlyLoading 
  } = useQuery({
    queryKey: ['monthly-performance'],
    queryFn: dashboardService.getMonthlyPerformance,
  });

  if (statsError || ordersError) {
    return (
      <Alert
        message="Veri yüklenirken hata oluştu"
        description="Backend sunucusunun çalıştığından emin olun (http://localhost:8000)"
        type="error"
        showIcon
      />
    );
  }

  const statsCards = stats ? [
    { title: 'Aktif Siparişler', value: stats.aktif_siparisler, icon: <ShoppingCartOutlined />, color: '#1890ff' },
    { title: 'Üretimde', value: stats.uretimde, icon: <BuildOutlined />, color: '#52c41a' },
    { title: 'Tamamlanan', value: stats.tamamlanan, icon: <CheckCircleOutlined />, color: '#faad14' },
    { title: 'Bekleyen', value: stats.bekleyen, icon: <ClockCircleOutlined />, color: '#f5222d' },
    { title: 'Toplam Müşteri', value: stats.toplam_musteri, icon: <UserOutlined />, color: '#722ed1' },
    { title: 'Toplam Ürün', value: stats.toplam_urun, icon: <InboxOutlined />, color: '#13c2c2' },
  ] : [];

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Dashboard</Title>
      
      {/* İstatistik Kartları */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {statsLoading ? (
          <Col span={24}>
            <Card>
              <Spin size="large" />
            </Card>
          </Col>
        ) : (
          statsCards.map((stat, index) => (
            <Col xs={24} sm={12} lg={4} key={index}>
              <Card>
                <Statistic
                  title={stat.title}
                  value={stat.value}
                  prefix={React.cloneElement(stat.icon, { style: { color: stat.color } })}
                  valueStyle={{ color: stat.color }}
                />
              </Card>
            </Col>
          ))
        )}
      </Row>

      <Row gutter={[16, 16]}>
        {/* Sipariş Durumu Grafiği */}
        <Col xs={24} lg={12}>
          <StyledCard title="Sipariş Durumu" size="small">
            {statusLoading ? (
              <Spin size="large" />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  >
                    {statusDistribution?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </StyledCard>
        </Col>

        {/* Aylık Performans */}
        <Col xs={24} lg={12}>
          <StyledCard title="Aylık Performans" size="small">
            {monthlyLoading ? (
              <Spin size="large" />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyPerformance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="siparisler" fill="#1890ff" name="Siparişler" />
                  <Bar dataKey="uretim" fill="#52c41a" name="Üretim" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </StyledCard>
        </Col>

        {/* Son Siparişler */}
        <Col xs={24}>
          <Card title="Son Siparişler" size="small">
            {ordersLoading ? (
              <Spin size="large" />
            ) : (
              <List
                itemLayout="horizontal"
                dataSource={recentOrders || []}
                renderItem={(item: any) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Avatar style={{ backgroundColor: '#1890ff' }}>
                          {item.siparis_no.replace(/\D/g, '').slice(-2) || 'S'}
                        </Avatar>
                      }
                      title={item.siparis_no}
                      description={`Müşteri ID: ${item.musteri} • Teslim: ${new Date(item.teslim_tarihi).toLocaleDateString('tr-TR')}`}
                    />
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ minWidth: '120px' }}>
                        {statusDisplayMap[item.durum] || item.durum}
                      </span>
                      <Progress 
                        percent={statusProgressMap[item.durum] || 0} 
                        size="small" 
                        style={{ width: '120px' }}
                        strokeColor={statusProgressMap[item.durum] === 100 ? '#52c41a' : '#1890ff'}
                      />
                      <span style={{ minWidth: '80px', color: '#666' }}>
                        {item.toplam_tutar?.toLocaleString('tr-TR') || '0'} TL
                      </span>
                    </div>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;