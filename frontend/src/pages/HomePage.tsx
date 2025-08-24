import React from 'react';
import { Row, Col, Card, Typography, Space, Button } from 'antd';
import { 
  ShoppingCartOutlined, 
  ShoppingOutlined, 
  BuildOutlined, 
  BarChartOutlined,
  ArrowRightOutlined,
  DashboardOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const { Title, Paragraph } = Typography;

const HeroSection = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 24px;
  text-align: center;
  margin: -24px -24px 40px -24px;
  border-radius: 0 0 16px 16px;
  
  .dark-theme & {
    background: linear-gradient(135deg, #4c6ef5 0%, #845ef7 100%);
  }
`;

const ModuleCard = styled(Card)`
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    border-color: #1890ff;
  }
  
  .ant-card-head {
    background: linear-gradient(135deg, #f0f8ff 0%, #e6f7ff 100%);
  }
  
  .module-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: #1890ff;
  }
`;

const StatsRow = styled(Row)`
  margin: 40px 0;
`;

const StatCard = styled(Card)`
  text-align: center;
  
  .stat-number {
    font-size: 32px;
    font-weight: bold;
    color: #1890ff;
    margin-bottom: 8px;
  }
  
  .stat-label {
    color: #666;
    font-size: 14px;
  }
`;

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const modules = [
    {
      key: 'sales',
      title: 'Satış',
      description: 'Müşteri siparişleri, teklif yönetimi ve satış takibi',
      icon: <ShoppingCartOutlined />,
      color: '#52c41a',
      path: '/sales',
      features: ['Sipariş Yönetimi', 'Müşteri Takibi', 'Teslim Tarihleri', 'Fiyat Listesi']
    },
    {
      key: 'procurement',
      title: 'Satın Alma',
      description: 'Tedarikçi yönetimi, satın alma siparişleri ve malzeme takibi',
      icon: <ShoppingOutlined />,
      color: '#1890ff',
      path: '/procurement',
      features: ['Tedarikçi Yönetimi', 'Malzeme İhtiyaç Planlama', 'Satın Alma Siparişleri', 'Fiyat Karşılaştırması']
    },
    {
      key: 'production',
      title: 'Üretim',
      description: 'Üretim planlama, iş emirleri ve kapasite yönetimi',
      icon: <BuildOutlined />,
      color: '#722ed1',
      path: '/production',
      features: ['İş Emri Yönetimi', 'Kapasite Planlama', 'Üretim Takibi', 'Kalite Kontrol']
    },
    {
      key: 'reports',
      title: 'Yönetim Raporları',
      description: 'Performans analitiği, mali raporlar ve karar destek sistemi',
      icon: <BarChartOutlined />,
      color: '#fa8c16',
      path: '/reports',
      features: ['Mali Raporlar', 'Performans KPI\'ları', 'Trend Analizi', 'Excel Export']
    }
  ];

  const quickStats = [
    { label: 'Aktif Siparişler', value: '24', color: '#1890ff' },
    { label: 'Üretimde', value: '8', color: '#52c41a' },
    { label: 'Bekleyen Tedarik', value: '12', color: '#fa8c16' },
    { label: 'Teslim Edilen', value: '156', color: '#722ed1' }
  ];

  return (
    <div>
      <HeroSection>
        <DashboardOutlined style={{ fontSize: '64px', marginBottom: '24px' }} />
        <Title level={1} style={{ color: 'white', marginBottom: '16px' }}>
          Üretim Planlama Sistemi
        </Title>
        <Paragraph style={{ fontSize: '18px', color: 'white', opacity: 0.9, marginBottom: '32px' }}>
          Entegre üretim yönetimi çözümü ile siparişten teslimat sürecinizi optimize edin
        </Paragraph>
        <Space size="large">
          <Button 
            type="primary" 
            size="large" 
            icon={<ArrowRightOutlined />}
            onClick={() => navigate('/dashboard')}
          >
            Genel Dashboard
          </Button>
          <Button 
            size="large" 
            style={{ background: 'rgba(255,255,255,0.2)', borderColor: 'white', color: 'white' }}
            onClick={() => navigate('/visual-editor')}
          >
            Sayfa Editörü
          </Button>
        </Space>
      </HeroSection>

      {/* Hızlı İstatistikler */}
      <StatsRow gutter={[16, 16]}>
        {quickStats.map((stat, index) => (
          <Col xs={12} sm={6} key={index}>
            <StatCard>
              <div className="stat-number" style={{ color: stat.color }}>
                {stat.value}
              </div>
              <div className="stat-label">{stat.label}</div>
            </StatCard>
          </Col>
        ))}
      </StatsRow>

      {/* Ana Modüller */}
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        Sistem Modülleri
      </Title>

      <Row gutter={[24, 24]}>
        {modules.map(module => (
          <Col xs={24} sm={12} lg={6} key={module.key}>
            <ModuleCard 
              hoverable 
              onClick={() => navigate(module.path)}
              title={
                <Space>
                  <span style={{ color: module.color }}>
                    {React.cloneElement(module.icon, { style: { fontSize: '20px' } })}
                  </span>
                  {module.title}
                </Space>
              }
              actions={[
                <Button 
                  type="link" 
                  icon={<ArrowRightOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(module.path);
                  }}
                >
                  Modüle Git
                </Button>
              ]}
            >
              <div style={{ textAlign: 'center', padding: '16px 0' }}>
                <div className="module-icon" style={{ color: module.color }}>
                  {module.icon}
                </div>
                <Paragraph style={{ marginBottom: '16px', minHeight: '48px' }}>
                  {module.description}
                </Paragraph>
                <div style={{ textAlign: 'left' }}>
                  <Title level={5} style={{ marginBottom: '8px' }}>Özellikler:</Title>
                  <ul style={{ paddingLeft: '16px', margin: 0 }}>
                    {module.features.map((feature, idx) => (
                      <li key={idx} style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </ModuleCard>
          </Col>
        ))}
      </Row>

      {/* Alt Bilgi */}
      <div style={{ 
        marginTop: '60px', 
        padding: '24px', 
        background: '#fafafa', 
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <Paragraph style={{ margin: 0, color: '#666' }}>
          📧 Destek için: support@uretimplanlama.com | 📞 +90 212 xxx xx xx
        </Paragraph>
      </div>
    </div>
  );
};

export default HomePage;