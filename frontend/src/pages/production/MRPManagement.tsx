import React from 'react';
import { Card, Table, Button, Space, Tag, Row, Col, Statistic, Typography, Divider, Alert, Progress, List } from 'antd';
import { 
  ShoppingOutlined, 
  PlusOutlined, 
  EyeOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import styled from 'styled-components';

const { Title } = Typography;

const PageHeader = styled.div`
  background: linear-gradient(135deg, #722ed1 0%, #531dab 100%);
  color: white;
  padding: 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 8px 8px;
`;

const MRPManagement: React.FC = () => {
  const navigate = useNavigate();

  // MRP verilerini çek
  const { data: mrpData, isLoading: mrpLoading } = useQuery({
    queryKey: ['mrp-stats'],
    queryFn: productionService.getMRPStats
  });

  // Mock material requirements data
  const materialRequirements = [
    {
      id: 1,
      material: 'Çelik Sac 2mm',
      required: 1500,
      available: 800,
      shortage: 700,
      unit: 'kg',
      supplier: 'Çelik A.Ş.',
      leadTime: 5,
      status: 'urgent'
    },
    {
      id: 2,
      material: 'Bakır Tel 16mm',
      required: 2000,
      available: 1800,
      shortage: 200,
      unit: 'metre',
      supplier: 'Metal Ltd.',
      leadTime: 3,
      status: 'normal'
    },
    {
      id: 3,
      material: 'Transformatör Yağı',
      required: 500,
      available: 100,
      shortage: 400,
      unit: 'litre',
      supplier: 'Yağ Sanayi',
      leadTime: 7,
      status: 'critical'
    },
    {
      id: 4,
      material: 'Alüminyum Folyo',
      required: 300,
      available: 350,
      shortage: 0,
      unit: 'kg',
      supplier: 'Folyo A.Ş.',
      leadTime: 2,
      status: 'sufficient'
    }
  ];

  const columns = [
    {
      title: 'Malzeme',
      dataIndex: 'material',
      key: 'material',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Gerekli',
      dataIndex: 'required',
      key: 'required',
      render: (value: number, record: any) => `${value} ${record.unit}`
    },
    {
      title: 'Mevcut',
      dataIndex: 'available',
      key: 'available',
      render: (value: number, record: any) => `${value} ${record.unit}`
    },
    {
      title: 'Eksik',
      key: 'shortage',
      render: (record: any) => (
        <div>
          <strong style={{ color: record.shortage > 0 ? '#ff4d4f' : '#52c41a' }}>
            {record.shortage > 0 ? `${record.shortage} ${record.unit}` : 'Yeterli'}
          </strong>
          {record.shortage > 0 && (
            <Progress 
              percent={Math.round((record.available / record.required) * 100)} 
              size="small" 
              style={{ marginTop: 4 }}
            />
          )}
        </div>
      )
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          critical: { color: 'error', text: 'Kritik', icon: <ExclamationCircleOutlined /> },
          urgent: { color: 'warning', text: 'Acil', icon: <WarningOutlined /> },
          normal: { color: 'processing', text: 'Normal', icon: <ClockCircleOutlined /> },
          sufficient: { color: 'success', text: 'Yeterli', icon: <CheckCircleOutlined /> }
        };
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: 'Tedarikçi',
      dataIndex: 'supplier',
      key: 'supplier'
    },
    {
      title: 'Teslimat Süresi',
      dataIndex: 'leadTime',
      key: 'leadTime',
      render: (days: number) => `${days} gün`
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (record: any) => (
        <Space>
          <Button type="primary" size="small" icon={<ShoppingOutlined />}>
            Satın Al
          </Button>
          <Button size="small" icon={<EyeOutlined />}>
            Detay
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <PageHeader>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          <ShoppingOutlined style={{ marginRight: '12px' }} />
          Malzeme İhtiyaç Planlaması (MRP)
        </Title>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
          Sipariş bazlı malzeme ihtiyaçlarını planlayın ve yönetin
        </p>
      </PageHeader>

      {/* Uyarılar */}
      <Space direction="vertical" style={{ width: '100%', marginBottom: '24px' }}>
        <Alert
          message="Kritik Malzeme Eksikliği"
          description="2 malzeme kritik seviyede eksik. Acil satın alma gerekiyor."
          type="error"
          showIcon
          action={
            <Button size="small" danger>
              Acil Satın Al
            </Button>
          }
        />
      </Space>

      {/* MRP İstatistikleri */}
      {!mrpLoading && mrpData && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Planlanan Siparişler"
                value={mrpData.plannedOrders}
                prefix={<ClockCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Malzeme Bekleyen"
                value={mrpData.waitingMaterials}
                prefix={<WarningOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Üretimde"
                value={mrpData.inProduction}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="Geciken Siparişler"
                value={mrpData.delayedOrders}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Kritik Malzemeler */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={8}>
          <Card title="Kritik Malzemeler" size="small">
            {!mrpLoading && mrpData && (
              <List
                size="small"
                dataSource={mrpData.criticalMaterials}
                renderItem={(item: any) => (
                  <List.Item>
                    <div>
                      <strong>{item.name}</strong>
                      <br />
                      <span style={{ color: '#ff4d4f' }}>
                        Eksik: {item.shortage} {item.unit}
                      </span>
                    </div>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={16}>
          <Card title="Hızlı İşlemler">
            <Space wrap>
              <Button type="primary" icon={<PlusOutlined />}>
                MRP Çalıştır
              </Button>
              <Button icon={<ShoppingOutlined />}>
                Toplu Satın Alma
              </Button>
              <Button icon={<EyeOutlined />}>
                Malzeme Raporu
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Malzeme İhtiyaçları Tablosu */}
      <Card 
        title="Malzeme İhtiyaçları"
        extra={
          <Space>
            <Button icon={<PlusOutlined />}>
              Manuel Ekle
            </Button>
            <Button type="primary" icon={<ShoppingOutlined />}>
              Satın Alma Emri Oluştur
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={materialRequirements}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} / ${total} malzeme`
          }}
        />
      </Card>

      {/* Geri Dön Butonu */}
      <Divider />
      <Space>
        <Button onClick={() => navigate('/production')}>
          ← Üretim Dashboard'a Dön
        </Button>
        <Button type="primary" onClick={() => navigate('/production/workflows')}>
          İş Akışlarına Git →
        </Button>
      </Space>
    </div>
  );
};

export default MRPManagement;