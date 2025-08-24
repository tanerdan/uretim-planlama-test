import React from 'react';
import { Row, Col, Card, Statistic, Typography, List, Progress, Button, Table, Tag } from 'antd';
import { 
  ShoppingOutlined, 
  UserOutlined, 
  DollarOutlined, 
  TruckOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  FileSearchOutlined
} from '@ant-design/icons';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import styled from 'styled-components';

const { Title } = Typography;

const ModuleHeader = styled.div`
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
  padding: 32px 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 12px 12px;
  
  .dark-theme & {
    background: linear-gradient(135deg, #339af0 0%, #1c7ed6 100%);
  }
`;

const ActionCard = styled(Card)`
  .ant-card-body {
    padding: 16px;
    text-align: center;
  }
  
  &:hover {
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
    transform: translateY(-2px);
    transition: all 0.3s ease;
  }
`;

const ProcurementDashboard: React.FC = () => {
  const procurementStats = [
    { title: 'Aktif Tedarikçiler', value: 28, prefix: <UserOutlined />, color: '#1890ff' },
    { title: 'Bekleyen Siparişler', value: 15, prefix: <ClockCircleOutlined />, color: '#fa8c16' },
    { title: 'Aylık Harcama', value: '₺1.8M', prefix: <DollarOutlined />, color: '#722ed1' },
    { title: 'Teslimat Oranı', value: '92%', prefix: <TruckOutlined />, color: '#52c41a' },
  ];

  const supplierPerformance = [
    { name: 'A Sınıfı', value: 65, color: '#52c41a' },
    { name: 'B Sınıfı', value: 25, color: '#fa8c16' },
    { name: 'C Sınıfı', value: 10, color: '#f5222d' },
  ];

  const pendingOrders = [
    { 
      id: 'SA-2025-001', 
      supplier: 'ABC Malzeme Ltd.', 
      items: 'Bakır Tel - 500kg',
      amount: '₺85,000', 
      deadline: '2025-08-25',
      status: 'bekleyen',
      delay: 0
    },
    { 
      id: 'SA-2025-002', 
      supplier: 'XYZ Kimya A.Ş.', 
      items: 'Trafo Yağı - 200L',
      amount: '₺24,500', 
      deadline: '2025-08-22',
      status: 'geciken',
      delay: 2
    },
    { 
      id: 'SA-2025-003', 
      supplier: 'DEF Elektrik', 
      items: 'İzolasyon Malz. - 100m',
      amount: '₺15,800', 
      deadline: '2025-08-28',
      status: 'yolda',
      delay: 0
    },
  ];

  const materialCategories = [
    { category: 'Elektrik Malz.', spent: 450000, budget: 500000, orders: 12 },
    { category: 'Mekanik Parça', spent: 320000, budget: 350000, orders: 8 },
    { category: 'Kimyasallar', spent: 180000, budget: 200000, orders: 6 },
    { category: 'Ambalaj', spent: 95000, budget: 120000, orders: 4 },
  ];

  const quickActions = [
    { title: 'Satın Alma Talebi', icon: <PlusOutlined />, color: '#1890ff' },
    { title: 'Tedarikçi Değerlendir', icon: <FileSearchOutlined />, color: '#52c41a' },
    { title: 'Fiyat Karşılaştır', icon: <DollarOutlined />, color: '#722ed1' },
    { title: 'Stok Kontrol', icon: <WarningOutlined />, color: '#fa8c16' },
  ];

  const columns = [
    { title: 'Sipariş No', dataIndex: 'id', key: 'id' },
    { title: 'Tedarikçi', dataIndex: 'supplier', key: 'supplier' },
    { title: 'Malzemeler', dataIndex: 'items', key: 'items' },
    { title: 'Tutar', dataIndex: 'amount', key: 'amount' },
    { 
      title: 'Durum', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string, record: any) => {
        let color = status === 'geciken' ? 'volcano' : 
                    status === 'yolda' ? 'geekblue' : 'blue';
        let text = status === 'geciken' ? `Geciken (${record.delay} gün)` :
                   status === 'yolda' ? 'Yolda' : 'Bekleyen';
        return <Tag color={color}>{text}</Tag>;
      }
    },
  ];

  return (
    <div>
      <ModuleHeader>
        <Title level={2} style={{ color: 'white', marginBottom: '8px' }}>
          <ShoppingOutlined /> Satın Alma Modülü
        </Title>
        <p style={{ color: 'rgba(255,255,255,0.8)', margin: 0 }}>
          Tedarikçi yönetimi, satın alma siparişleri ve malzeme takibi
        </p>
      </ModuleHeader>

      {/* İstatistikler */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {procurementStats.map((stat, index) => (
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
              <ActionCard hoverable>
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
        {/* Tedarikçi Performansı */}
        <Col xs={24} lg={8}>
          <Card title="Tedarikçi Performansı" size="small">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={supplierPerformance}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} %${(percent * 100).toFixed(0)}`}
                >
                  {supplierPerformance.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Malzeme Kategorisi Bütçe */}
        <Col xs={24} lg={16}>
          <Card title="Kategori Bazlı Harcama Durumu" size="small">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={materialCategories}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip formatter={(value) => [`₺${(value / 1000).toFixed(0)}K`]} />
                <Bar dataKey="spent" fill="#1890ff" name="Harcanan" />
                <Bar dataKey="budget" fill="#52c41a" name="Bütçe" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Bekleyen Siparişler Tablosu */}
        <Col xs={24}>
          <Card 
            title="Bekleyen Satın Alma Siparişleri" 
            size="small"
            extra={<Button type="primary">Yeni Sipariş</Button>}
          >
            <Table 
              columns={columns} 
              dataSource={pendingOrders} 
              pagination={false}
              size="small"
              rowKey="id"
            />
          </Card>
        </Col>

        {/* Kritik Stok Durumu */}
        <Col xs={24} lg={12}>
          <Card title="Kritik Stok Uyarıları" size="small">
            <List
              itemLayout="horizontal"
              dataSource={[
                { material: 'Bakır İletken', current: 50, minimum: 100, unit: 'kg' },
                { material: 'Trafo Yağı', current: 25, minimum: 50, unit: 'L' },
                { material: 'İzolasyon Bandı', current: 15, minimum: 30, unit: 'rulo' },
              ]}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<WarningOutlined style={{ color: '#fa8c16', fontSize: '18px' }} />}
                    title={item.material}
                    description={`Mevcut: ${item.current} ${item.unit} / Min: ${item.minimum} ${item.unit}`}
                  />
                  <Progress 
                    percent={Math.round((item.current / item.minimum) * 100)}
                    size="small"
                    strokeColor={item.current < item.minimum ? '#f5222d' : '#52c41a'}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Bu Ayki Teslimatlar */}
        <Col xs={24} lg={12}>
          <Card title="Bu Ay Teslim Edilen" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic 
                  title="Zamanında" 
                  value={23} 
                  suffix="/ 25"
                  prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Gecikmeli" 
                  value={2} 
                  suffix="/ 25"
                  prefix={<ClockCircleOutlined style={{ color: '#f5222d' }} />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <Progress 
                percent={92} 
                strokeColor="#52c41a"
                format={() => 'Teslimat Başarı Oranı: %92'}
              />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ProcurementDashboard;