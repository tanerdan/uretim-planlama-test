import React from 'react';
import { Row, Col, Card, Statistic, Typography, List, Progress, Button, Space, Table, Alert } from 'antd';
import { 
  ToolOutlined, 
  SettingOutlined, 
  DeploymentUnitOutlined, 
  BuildOutlined,
  ForkOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  EyeOutlined,
  BarChartOutlined,
  StopOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  ApartmentOutlined,
  RocketOutlined,
  FileTextOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import dayjs from 'dayjs';

const { Title } = Typography;

const ModuleHeader = styled.div`
  background: linear-gradient(135deg, #722ed1 0%, #531dab 100%);
  color: white;
  padding: 32px 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 12px 12px;
  
  .dark-theme & {
    background: linear-gradient(135deg, #9c88ff 0%, #7c4dff 100%);
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
    box-shadow: 0 4px 12px rgba(114, 46, 209, 0.15);
    transform: translateY(-2px);
    transition: all 0.3s ease;
  }
`;

const ProductionDashboard: React.FC = () => {
  const navigate = useNavigate();
  
  // API data fetching
  const { data: bomData, isLoading: bomLoading } = useQuery({
    queryKey: ['production-bom'],
    queryFn: () => productionService.getBOMStats()
  });

  const { data: workflowData, isLoading: workflowLoading } = useQuery({
    queryKey: ['production-workflows'],
    queryFn: () => productionService.getWorkflowStats()
  });

  const { data: stationData, isLoading: stationLoading } = useQuery({
    queryKey: ['production-stations'],
    queryFn: () => productionService.getStationStats()
  });

  const { data: mrpData, isLoading: mrpLoading } = useQuery({
    queryKey: ['production-mrp'],
    queryFn: () => productionService.getMRPStats()
  });

  const { data: operationsData, isLoading: operationsLoading } = useQuery({
    queryKey: ['production-operations'],
    queryFn: () => productionService.getOperationsStats()
  });

  const isLoading = bomLoading || workflowLoading || stationLoading || mrpLoading || operationsLoading;

  // Helper function for number formatting
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Main statistics
  const mainStats = [
    { 
      title: 'Aktif BOM Reçeteleri', 
      value: formatNumber(bomData?.totalBOM || 0), 
      prefix: <ApartmentOutlined />, 
      color: '#722ed1' 
    },
    { 
      title: 'İş Akışları', 
      value: formatNumber(workflowData?.totalWorkflows || 0), 
      prefix: <ForkOutlined />, 
      color: '#52c41a' 
    },
    { 
      title: 'İş İstasyonları', 
      value: formatNumber(stationData?.totalStations || 0), 
      prefix: <ToolOutlined />, 
      color: '#1890ff' 
    },
    { 
      title: 'Standart İş Adımları', 
      value: formatNumber(operationsData?.totalOperations || 0), 
      prefix: <SettingOutlined />, 
      color: '#fa8c16' 
    },
  ];

  // Configuration and Setup Actions
  const configActions = [
    { 
      title: 'İstasyon Yönetimi', 
      icon: <ToolOutlined />, 
      action: () => navigate('/production/stations'), 
      color: '#fa8c16',
      description: 'İş istasyonları ve kapasiteler'
    },
    { 
      title: 'Ürün Reçeteleri (BOM)', 
      icon: <BuildOutlined />, 
      action: () => navigate('/production/bom'), 
      color: '#13c2c2',
      description: 'Ürün reçete yönetimi'
    },
    { 
      title: 'İş Akışı Tasarımı', 
      icon: <ApartmentOutlined />, 
      action: () => navigate('/production/workflows'), 
      color: '#52c41a',
      description: 'Görsel iş akışı editörü'
    },
  ];

  // Operations and Planning Actions
  const operationActions = [
    { 
      title: 'Malzeme Planlama (MRP)', 
      icon: <DeploymentUnitOutlined />, 
      action: () => navigate('/production/mrp'), 
      color: '#722ed1',
      description: 'Malzeme ihtiyaç planlaması'
    },
    { 
      title: 'İş Emirleri', 
      icon: <FileTextOutlined />, 
      action: () => navigate('/production/work-orders'), 
      color: '#1890ff',
      description: 'Üretim emirlerini yönet'
    },
  ];

  // Production status distribution
  const productionStatusData = [
    { name: 'Beklemede', value: mrpData?.plannedOrders || 0, color: '#1890ff' },
    { name: 'Malzeme Planlandı', value: mrpData?.waitingMaterials || 0, color: '#faad14' },
    { name: 'İş Emirleri Hazır', value: mrpData?.readyOrders || 0, color: '#52c41a' },
    { name: 'Üretimde', value: mrpData?.inProduction || 0, color: '#722ed1' },
    { name: 'Tamamlandı', value: mrpData?.completed || 0, color: '#13c2c2' },
  ].filter(item => item.value > 0);

  // Station capacity utilization
  const stationCapacityData = stationData?.capacityData || [];

  // Recent BOM updates
  const recentBOM = bomData?.recentBOM || [];

  // Recent workflows
  const recentWorkflows = workflowData?.recentWorkflows || [];

  // Production efficiency data
  const efficiencyData = [
    { month: 'Oca', verimlilik: 85, kapasite: 78 },
    { month: 'Şub', verimlilik: 88, kapasite: 82 },
    { month: 'Mar', verimlilik: 92, kapasite: 85 },
    { month: 'Nis', verimlilik: 89, kapasite: 88 },
    { month: 'May', verimlilik: 94, kapasite: 91 },
    { month: 'Haz', verimlilik: 96, kapasite: 93 },
  ];

  // Critical materials
  const criticalMaterials = mrpData?.criticalMaterials || [];

  return (
    <div>
      <ModuleHeader>
        <Title level={2} className="module-title">
          <BuildOutlined /> Üretim Planlama Modülü
        </Title>
        <p className="module-desc">
          MRP, iş akışları, üretim emirleri ve kapasite planlama yönetimi
        </p>
      </ModuleHeader>

      {/* Critical materials alert */}
      {criticalMaterials.length > 0 && (
        <Alert
          message={`${criticalMaterials.length} kritik malzeme eksikliği tespit edildi!`}
          description={
            <div>
              Eksik malzemeler: {criticalMaterials.slice(0, 3).map(m => m.name).join(', ')}
              {criticalMaterials.length > 3 && ` ve ${criticalMaterials.length - 3} daha...`}
            </div>
          }
          type="error"
          showIcon
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: '24px' }}
          action={
            <Button size="small" danger onClick={() => navigate('/production/mrp')}>
              MRP'ye Git
            </Button>
          }
        />
      )}

      {/* Main Statistics */}
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

      {/* Quick Actions - Grouped */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {/* Configuration and Setup */}
        <Col xs={24} lg={12}>
          <Card title="Yapılandırma ve Kurulum" size="small">
            <Row gutter={[12, 12]}>
              {configActions.map((action, index) => (
                <Col xs={24} sm={12} lg={8} key={index}>
                  <ActionCard hoverable onClick={action.action} size="small">
                    <div style={{ color: action.color, fontSize: '28px', marginBottom: '8px' }}>
                      {action.icon}
                    </div>
                    <div style={{ fontWeight: 'bold', marginBottom: '2px', fontSize: '13px' }}>{action.title}</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>{action.description}</div>
                  </ActionCard>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* Operations and Planning */}
        <Col xs={24} lg={12}>
          <Card title="Operasyon ve Planlama" size="small">
            <Row gutter={[12, 12]}>
              {operationActions.map((action, index) => (
                <Col xs={24} sm={12} key={index}>
                  <ActionCard hoverable onClick={action.action} size="small">
                    <div style={{ color: action.color, fontSize: '28px', marginBottom: '8px' }}>
                      {action.icon}
                    </div>
                    <div style={{ fontWeight: 'bold', marginBottom: '2px', fontSize: '13px' }}>{action.title}</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>{action.description}</div>
                  </ActionCard>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Production Status Distribution */}
        <Col xs={24} lg={12}>
          <Card title="Üretim Durumu Dağılımı" size="small" loading={isLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={productionStatusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {productionStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Station Capacity Utilization */}
        <Col xs={24} lg={12}>
          <Card title="İstasyon Kapasite Kullanımı" size="small" loading={isLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stationCapacityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [`%${value}`, 'Kapasite Kullanımı']} />
                <Bar dataKey="utilization" fill="#722ed1" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Recent BOM Updates */}
        <Col xs={24} lg={12}>
          <Card 
            title="Son Güncelenen Reçeteler" 
            size="small" 
            loading={isLoading}
            extra={<Button type="link" onClick={() => navigate('/production/bom')}>Tümünü Gör</Button>}
          >
            <List
              itemLayout="horizontal"
              dataSource={recentBOM}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<ApartmentOutlined style={{ color: '#722ed1', fontSize: '16px' }} />}
                    title={
                      <Button 
                        type="link" 
                        onClick={() => navigate(`/production/bom/${item.id}`)}
                        style={{ padding: 0, fontWeight: 'bold' }}
                      >
                        {item.name}
                      </Button>
                    }
                    description={`${item.components} bileşen • ${dayjs(item.updated).format('DD.MM.YYYY')}`}
                  />
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', color: '#666' }}>{item.type}</div>
                  </div>
                </List.Item>
              )}
              locale={{ emptyText: 'Henüz reçete bulunmuyor' }}
            />
          </Card>
        </Col>

        {/* Production Efficiency Trend */}
        <Col xs={24} lg={12}>
          <Card title="Son 6 Ay Üretim Verimliliği" size="small" loading={isLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={efficiencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value, name) => [`%${value}`, name === 'verimlilik' ? 'Verimlilik' : 'Kapasite Kullanımı']} />
                <Line type="monotone" dataKey="verimlilik" stroke="#52c41a" name="verimlilik" />
                <Line type="monotone" dataKey="kapasite" stroke="#722ed1" name="kapasite" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Recent Workflows */}
        <Col xs={24} lg={12}>
          <Card 
            title="Son İş Akışları" 
            size="small"
            loading={isLoading}
            extra={<Button type="link" onClick={() => navigate('/production/workflows')}>Tümünü Gör</Button>}
          >
            <List
              itemLayout="horizontal"
              dataSource={recentWorkflows}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<ForkOutlined style={{ color: '#52c41a', fontSize: '16px' }} />}
                    title={
                      <Button 
                        type="link" 
                        onClick={() => navigate(`/production/workflows/${item.id}`)}
                        style={{ padding: 0, fontWeight: 'bold' }}
                      >
                        {item.name}
                      </Button>
                    }
                    description={`${item.operations} operasyon • ${item.product}`}
                  />
                  <div style={{ color: '#52c41a', fontSize: '12px' }}>
                    <CheckCircleOutlined /> Aktif
                  </div>
                </List.Item>
              )}
              locale={{ emptyText: 'Henüz iş akışı bulunmuyor' }}
            />
          </Card>
        </Col>

        {/* Production Metrics */}
        <Col xs={24} lg={12}>
          <Card title="Üretim Metrikleri" size="small" loading={isLoading}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic 
                  title="Bu Ay Tamamlanan" 
                  value={formatNumber(mrpData?.monthlyCompleted || 0)} 
                  prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                  suffix="iş emri"
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Geciken İşler" 
                  value={formatNumber(mrpData?.delayedOrders || 0)} 
                  prefix={<ClockCircleOutlined style={{ color: '#ff4d4f' }} />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <div style={{ marginBottom: '8px', fontSize: '14px', color: '#666' }}>
                Ortalama Teslim Süresi
              </div>
              <Statistic
                value={mrpData?.avgDeliveryTime || 0}
                suffix="gün"
                precision={1}
                valueStyle={{ fontSize: '18px', color: '#722ed1' }}
              />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ProductionDashboard;