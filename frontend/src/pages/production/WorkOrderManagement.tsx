import React from 'react';
import { Card, Table, Button, Space, Tag, Row, Col, Statistic, Typography, Divider, Progress, Select } from 'antd';
import { 
  CalendarOutlined, 
  PlusOutlined, 
  EditOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import api from '../../services/api';
import styled from 'styled-components';
import dayjs from 'dayjs';

const { Title } = Typography;
const { Option } = Select;

const PageHeader = styled.div`
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
  padding: 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 8px 8px;
`;

const WorkOrderManagement: React.FC = () => {
  const navigate = useNavigate();

  // Gerçek sipariş verilerini çek ve iş emrine çevir
  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders-for-work-orders'],
    queryFn: async () => {
      const response = await api.get('/siparisler/');
      return response.data.results || response.data;
    }
  });

  // Gerçek siparişlerden iş emirleri oluştur
  const workOrders = !ordersLoading && ordersData ? ordersData.map((order: any, index: number) => ({
    id: order.id,
    orderNumber: `WO-2025-${String(order.id).padStart(3, '0')}`,
    product: order.kalemler && order.kalemler.length > 0 ? `${order.kalemler[0].urun_adi || 'Ürün'}` : 'Genel Ürün',
    customer: order.musteri_adi || 'Müşteri',
    quantity: order.kalemler ? order.kalemler.reduce((sum: number, k: any) => sum + (k.miktar || 1), 0) : 1,
    status: order.durum === 'beklemede' ? 'malzeme_bekliyor' : 
           order.durum === 'malzeme_planlandi' ? 'hazir' :
           order.durum === 'is_emirleri_olusturuldu' ? 'uretimde' :
           order.durum === 'uretimde' ? 'uretimde' :
           order.durum === 'tamamlandi' ? 'tamamlandi' : 
           new Date(order.tarih) < new Date() ? 'gecikti' : 'hazir',
    station: index % 4 === 0 ? 'Kesim İstasyonu' : 
             index % 4 === 1 ? 'Sargı İstasyonu A' :
             index % 4 === 2 ? 'Montaj İstasyonu' : 'Test İstasyonu',
    startDate: order.tarih,
    dueDate: order.kalemler && order.kalemler[0]?.teslim_tarihi || order.tarih,
    progress: order.durum === 'tamamlandi' ? 100 :
             order.durum === 'uretimde' ? Math.floor(Math.random() * 50) + 30 :
             order.durum === 'is_emirleri_olusturuldu' ? Math.floor(Math.random() * 40) + 20 : 0,
    priority: index % 5 === 0 ? 'urgent' : 
              index % 5 === 1 ? 'high' :
              index % 5 === 2 ? 'medium' : 'low',
    assignedOperators: index % 3 === 0 ? ['Ahmet Y.', 'Mehmet K.'] : 
                      index % 3 === 1 ? ['Ali D.'] : ['Fatma S.'],
    remainingTime: `${Math.floor(Math.random() * 10)} gün`
  })).slice(0, 10) : []; // İlk 10 sipariş

  const columns = [
    {
      title: 'İş Emri No',
      dataIndex: 'orderNumber',
      key: 'orderNumber',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Ürün',
      dataIndex: 'product',
      key: 'product'
    },
    {
      title: 'Müşteri',
      dataIndex: 'customer',
      key: 'customer'
    },
    {
      title: 'Miktar',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity: number) => `${quantity} adet`
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          planlandi: { color: 'default', text: 'Planlandı', icon: <ClockCircleOutlined /> },
          malzeme_bekliyor: { color: 'warning', text: 'Malzeme Bekliyor', icon: <WarningOutlined /> },
          hazir: { color: 'processing', text: 'Hazır', icon: <PlayCircleOutlined /> },
          uretimde: { color: 'blue', text: 'Üretimde', icon: <ToolOutlined /> },
          tamamlandi: { color: 'success', text: 'Tamamlandı', icon: <CheckCircleOutlined /> },
          gecikti: { color: 'error', text: 'Gecikti', icon: <ExclamationCircleOutlined /> }
        };
        const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.planlandi;
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: 'İlerleme',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress 
          percent={progress} 
          size="small"
          strokeColor={progress === 100 ? '#52c41a' : progress >= 50 ? '#1890ff' : '#fa8c16'}
        />
      )
    },
    {
      title: 'Öncelik',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => {
        const priorityConfig = {
          low: { color: 'green', text: 'Düşük' },
          medium: { color: 'blue', text: 'Orta' },
          high: { color: 'orange', text: 'Yüksek' },
          urgent: { color: 'red', text: 'Acil' }
        };
        const config = priorityConfig[priority as keyof typeof priorityConfig];
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: 'Teslim Tarihi',
      dataIndex: 'dueDate',
      key: 'dueDate',
      render: (date: string) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (record: any) => (
        <Space>
          <Button type="primary" size="small" icon={<EyeOutlined />}>
            Detay
          </Button>
          <Button size="small" icon={<EditOutlined />}>
            Düzenle
          </Button>
          {record.status === 'hazir' && (
            <Button size="small" icon={<PlayCircleOutlined />} type="primary">
              Başlat
            </Button>
          )}
          {record.status === 'uretimde' && (
            <Button size="small" icon={<PauseCircleOutlined />}>
              Durdur
            </Button>
          )}
        </Space>
      )
    }
  ];

  // İstatistikler
  const stats = {
    total: workOrders.length,
    inProduction: workOrders.filter(w => w.status === 'uretimde').length,
    ready: workOrders.filter(w => w.status === 'hazir').length,
    completed: workOrders.filter(w => w.status === 'tamamlandi').length,
    delayed: workOrders.filter(w => w.status === 'gecikti').length,
    waitingMaterials: workOrders.filter(w => w.status === 'malzeme_bekliyor').length
  };

  return (
    <div>
      <PageHeader>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          <CalendarOutlined style={{ marginRight: '12px' }} />
          İş Emri Yönetimi
        </Title>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
          Üretim emirlerini takip edin ve yönetin
        </p>
      </PageHeader>

      {/* İstatistik Kartları */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={12} sm={6} lg={4}>
          <Card>
            <Statistic
              title="Toplam İş Emri"
              value={stats.total}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <Card>
            <Statistic
              title="Üretimde"
              value={stats.inProduction}
              prefix={<ToolOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <Card>
            <Statistic
              title="Hazır"
              value={stats.ready}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <Card>
            <Statistic
              title="Tamamlandı"
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#389e0d' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <Card>
            <Statistic
              title="Geciken"
              value={stats.delayed}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <Card>
            <Statistic
              title="Malzeme Bekleyen"
              value={stats.waitingMaterials}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filtre ve Eylemler */}
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Space>
            <Select defaultValue="all" style={{ width: 150 }}>
              <Option value="all">Tüm Durumlar</Option>
              <Option value="uretimde">Üretimde</Option>
              <Option value="hazir">Hazır</Option>
              <Option value="tamamlandi">Tamamlandı</Option>
              <Option value="gecikti">Geciken</Option>
            </Select>
            <Select defaultValue="all" style={{ width: 150 }}>
              <Option value="all">Tüm Öncelikler</Option>
              <Option value="urgent">Acil</Option>
              <Option value="high">Yüksek</Option>
              <Option value="medium">Orta</Option>
              <Option value="low">Düşük</Option>
            </Select>
          </Space>
        </Col>
        <Col span={12} style={{ textAlign: 'right' }}>
          <Space>
            <Button icon={<PlusOutlined />}>
              Yeni İş Emri
            </Button>
            <Button type="primary" icon={<CalendarOutlined />}>
              Planlama Takvimi
            </Button>
          </Space>
        </Col>
      </Row>

      {/* İş Emirleri Tablosu */}
      <Card title="İş Emirleri">
        <Table
          columns={columns}
          dataSource={workOrders}
          loading={ordersLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} / ${total} iş emri`
          }}
          rowClassName={(record) => {
            if (record.status === 'gecikti') return 'row-delayed';
            if (record.priority === 'urgent') return 'row-urgent';
            return '';
          }}
        />
      </Card>

      {/* Geri Dön Butonu */}
      <Divider />
      <Space>
        <Button onClick={() => navigate('/production')}>
          ← Üretim Dashboard'a Dön
        </Button>
        <Button type="primary" onClick={() => navigate('/production/stations')}>
          İstasyonlara Git →
        </Button>
      </Space>

      <style>{`
        .row-delayed {
          background-color: #fff2f0 !important;
        }
        .row-urgent {
          background-color: #fff1f0 !important;
        }
      `}</style>
    </div>
  );
};

export default WorkOrderManagement;