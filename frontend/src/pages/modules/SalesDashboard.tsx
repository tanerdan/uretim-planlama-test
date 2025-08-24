import React from 'react';
import { Row, Col, Card, Statistic, Typography, List, Progress, Button, Space, Table } from 'antd';
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
  BarChartOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

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
  // Mock data - gerçek API'lerle değiştirilecek
  const salesStats = [
    { title: 'Toplam Siparişler', value: 156, prefix: <ShoppingCartOutlined />, color: '#1890ff' },
    { title: 'Aktif Müşteriler', value: 34, prefix: <UserOutlined />, color: '#52c41a' },
    { title: 'Aylık Ciro', value: '₺2.4M', prefix: <DollarOutlined />, color: '#722ed1' },
    { title: 'Büyüme Oranı', value: '+15%', prefix: <RiseOutlined />, color: '#fa8c16' },
  ];

  const recentOrders = [
    { id: 'SIP-2025-001', customer: 'ABC Elektrik A.Ş.', amount: '₺125,000', status: 'Beklemede', progress: 10 },
    { id: 'SIP-2025-002', customer: 'XYZ Makina Ltd.', amount: '₺89,500', status: 'Üretimde', progress: 65 },
    { id: 'SIP-2025-003', customer: 'DEF Enerji A.Ş.', amount: '₺245,000', status: 'Sevkiyata Hazır', progress: 90 },
    { id: 'SIP-2025-004', customer: 'GHI Otomotiv', amount: '₺67,800', status: 'Teslim Edildi', progress: 100 },
  ];

  const monthlySales = [
    { month: 'Oca', siparisler: 45, ciro: 2100000 },
    { month: 'Şub', siparisler: 52, ciro: 2350000 },
    { month: 'Mar', siparisler: 48, ciro: 2200000 },
    { month: 'Nis', siparisler: 61, ciro: 2800000 },
    { month: 'May', siparisler: 55, ciro: 2600000 },
    { month: 'Haz', siparisler: 67, ciro: 3100000 },
  ];

  const quickActions = [
    { title: 'Yeni Sipariş', icon: <PlusOutlined />, action: () => navigate('/sales/orders/new'), color: '#52c41a' },
    { title: 'Siparişleri Görüntüle', icon: <EyeOutlined />, action: () => navigate('/sales/orders'), color: '#1890ff' },
    { title: 'Müşteri Ekle', icon: <UserOutlined />, action: () => navigate('/sales/customers/new'), color: '#722ed1' },
    { title: 'Raporlar', icon: <BarChartOutlined />, action: () => navigate('/sales/reports'), color: '#fa8c16' },
  ];

  const urgentOrders = [
    { id: 'SIP-2025-001', customer: 'ABC Elektrik', deadline: '3 gün', priority: 'high' },
    { id: 'SIP-2025-005', customer: 'MNO Sanayi', deadline: '1 hafta', priority: 'medium' },
    { id: 'SIP-2025-008', customer: 'PQR Elektrik', deadline: '2 hafta', priority: 'low' },
  ];

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

      {/* İstatistikler */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {salesStats.map((stat, index) => (
          <Col xs={12} sm={6} key={index}>
            <Card>
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
        {/* Aylık Satış Trendi */}
        <Col xs={24} lg={12}>
          <Card title="Aylık Satış Performansı" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlySales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value, name) => {
                  if (name === 'ciro') {
                    return [`₺${(value / 1000000).toFixed(1)}M`, 'Ciro'];
                  }
                  return [value, 'Sipariş Sayısı'];
                }} />
                <Line type="monotone" dataKey="siparisler" stroke="#1890ff" name="siparisler" />
                <Line type="monotone" dataKey="ciro" stroke="#52c41a" name="ciro" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Son Siparişler */}
        <Col xs={24} lg={12}>
          <Card title="Son Siparişler" size="small">
            <List
              itemLayout="horizontal"
              dataSource={recentOrders}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    title={<a href="#">{item.id}</a>}
                    description={item.customer}
                  />
                  <div style={{ textAlign: 'right', minWidth: '120px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{item.amount}</div>
                    <Progress 
                      percent={item.progress} 
                      size="small"
                      strokeColor={item.progress === 100 ? '#52c41a' : '#1890ff'}
                    />
                    <div style={{ fontSize: '12px', color: '#666' }}>{item.status}</div>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Acil Siparişler */}
        <Col xs={24} lg={12}>
          <Card 
            title="Acil Siparişler" 
            size="small"
            extra={<Button type="link">Tümünü Gör</Button>}
          >
            <List
              itemLayout="horizontal"
              dataSource={urgentOrders}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <div style={{ 
                        width: '8px', 
                        height: '8px', 
                        borderRadius: '50%',
                        backgroundColor: item.priority === 'high' ? '#ff4d4f' : 
                                       item.priority === 'medium' ? '#fa8c16' : '#52c41a'
                      }} />
                    }
                    title={item.id}
                    description={item.customer}
                  />
                  <div style={{ color: '#666', fontSize: '12px' }}>
                    <CalendarOutlined /> {item.deadline}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Müşteri Durumları */}
        <Col xs={24} lg={12}>
          <Card title="Müşteri Durumları" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic 
                  title="Aktif Müşteriler" 
                  value={34} 
                  prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Potansiyel" 
                  value={12} 
                  prefix={<ClockCircleOutlined style={{ color: '#fa8c16' }} />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <Progress 
                percent={74} 
                success={{ percent: 74 }} 
                format={() => 'Müşteri Memnuniyet Oranı: %74'}
              />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SalesDashboard;