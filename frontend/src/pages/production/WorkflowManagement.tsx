import React from 'react';
import { Card, Table, Button, Space, Tag, Row, Col, Typography, Divider, Modal, Steps } from 'antd';
import { 
  ForkOutlined, 
  PlusOutlined, 
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  ToolOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import styled from 'styled-components';

const { Title } = Typography;
const { Step } = Steps;

const PageHeader = styled.div`
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  color: white;
  padding: 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 8px 8px;
`;

const WorkflowManagement: React.FC = () => {
  const navigate = useNavigate();
  const [selectedWorkflow, setSelectedWorkflow] = React.useState<any>(null);
  const [previewVisible, setPreviewVisible] = React.useState(false);

  // Gerçek iş akışlarını çek
  const { data: workflowsData, isLoading: workflowsLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => productionService.getWorkflows()
  });

  // İş akışı verilerini formatla
  const workflows = workflowsData?.results || workflowsData || [];

  const columns = [
    {
      title: 'İş Akışı Adı',
      dataIndex: 'ad',
      key: 'ad',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Kod',
      dataIndex: 'kod',
      key: 'kod'
    },
    {
      title: 'Ürün',
      dataIndex: 'urun_adi',
      key: 'urun_adi'
    },
    {
      title: 'Operasyon Sayısı',
      dataIndex: 'operasyon_sayisi',
      key: 'operasyon_sayisi',
      render: (count: number) => (
        <Tag color="blue" icon={<ToolOutlined />}>
          {count || 0} Adım
        </Tag>
      )
    },
    {
      title: 'Versiyon',
      dataIndex: 'versiyon',
      key: 'versiyon',
      render: (version: string) => (
        <Tag color="blue">{version || '1.0'}</Tag>
      )
    },
    {
      title: 'Durum',
      dataIndex: 'aktif',
      key: 'aktif',
      render: (aktif: boolean) => {
        return aktif ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>Aktif</Tag>
        ) : (
          <Tag color="default">Pasif</Tag>
        );
      }
    },
    {
      title: 'Oluşturma',
      dataIndex: 'olusturulma_tarihi',
      key: 'olusturulma_tarihi',
      render: (date: string) => new Date(date).toLocaleDateString('tr-TR')
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (record: any) => (
        <Space>
          <Button 
            type="primary" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => showWorkflowPreview(record)}
          >
            Görüntüle
          </Button>
          <Button 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Düzenle
          </Button>
          <Button 
            danger 
            size="small" 
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            Sil
          </Button>
        </Space>
      )
    }
  ];

  const showWorkflowPreview = (workflow: any) => {
    setSelectedWorkflow(workflow);
    setPreviewVisible(true);
  };

  const handleEdit = (workflow: any) => {
    // Navigate to frontend workflow designer
    navigate(`/production/workflows/${workflow.id}/edit`);
  };

  const handleDelete = (workflow: any) => {
    if (confirm(`"${workflow.ad}" iş akışını silmek istediğinizden emin misiniz?`)) {
      // TODO: Implement API delete call
      alert('Silme işlemi henüz implement edilmedi. API call gereklidir.');
    }
  };

  const handleCreateNew = () => {
    // Navigate to frontend workflow designer
    navigate('/production/workflows/new');
  };

  return (
    <div>
      <PageHeader>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          <ForkOutlined style={{ marginRight: '12px' }} />
          İş Akışı Yönetimi
        </Title>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
          Ürün bazlı üretim süreçlerini tasarlayın ve yönetin
        </p>
      </PageHeader>

      {/* Özet Kartları */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                {workflows.filter(w => w.status === 'active').length}
              </div>
              <div>Aktif İş Akışı</div>
            </div>
          </Card>
        </Col>
        <Col xs={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fa8c16' }}>
                {workflows.filter(w => w.status === 'draft').length}
              </div>
              <div>Taslak İş Akışı</div>
            </div>
          </Card>
        </Col>
        <Col xs={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                {workflows.reduce((acc, w) => acc + w.operationCount, 0)}
              </div>
              <div>Toplam Operasyon</div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* İş Akışları Tablosu */}
      <Card 
        title="İş Akışları"
        extra={
          <Space>
            <Button 
              icon={<PlusOutlined />}
              onClick={handleCreateNew}
            >
              Yeni İş Akışı
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={workflows}
          loading={workflowsLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} / ${total} iş akışı`
          }}
        />
      </Card>

      {/* İş Akışı Önizleme Modal */}
      <Modal
        title={selectedWorkflow?.name}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setPreviewVisible(false)}>
            Kapat
          </Button>,
          <Button key="edit" type="primary" icon={<EditOutlined />}>
            Düzenle
          </Button>
        ]}
        width={800}
      >
        {selectedWorkflow && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <strong>Ürün:</strong> {selectedWorkflow.urun_adi}
              </Col>
              <Col span={8}>
                <strong>Operasyon Sayısı:</strong> {selectedWorkflow.operasyon_sayisi || 0}
              </Col>
              <Col span={8}>
                <strong>Versiyon:</strong> {selectedWorkflow.versiyon}
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <strong>Kod:</strong> {selectedWorkflow.kod}
              </Col>
              <Col span={8}>
                <strong>Tip:</strong> {selectedWorkflow.tip === 'seri' ? 'Seri İşlem' : 'Paralel İşlem'}
              </Col>
              <Col span={8}>
                <strong>Durum:</strong> {selectedWorkflow.aktif ? 'Aktif' : 'Pasif'}
              </Col>
            </Row>
            
            <Divider />
            
            <Title level={4}>Operasyon Adımları</Title>
            {selectedWorkflow.operasyonlar && selectedWorkflow.operasyonlar.length > 0 ? (
              <Steps direction="vertical">
                {selectedWorkflow.operasyonlar.map((operation: any) => (
                  <Step 
                    key={operation.id}
                    title={operation.operasyon_adi}
                    description={
                      <div>
                        <div><strong>İstasyon:</strong> {operation.istasyon_adi}</div>
                        <div><strong>Standart Süre:</strong> {operation.standart_sure} dakika</div>
                        <div><strong>Hazırlık Süresi:</strong> {operation.hazirlik_suresi} dakika</div>
                        <div><strong>Sıra No:</strong> {operation.sira_no}</div>
                        {operation.aciklama && <div><strong>Açıklama:</strong> {operation.aciklama}</div>}
                      </div>
                    }
                    icon={<ToolOutlined />}
                  />
                ))}
              </Steps>
            ) : (
              <div style={{ textAlign: 'center', color: '#666', padding: '32px' }}>
                Bu iş akışında henüz operasyon tanımlanmamış
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Geri Dön Butonu */}
      <Divider />
      <Space>
        <Button onClick={() => navigate('/production')}>
          ← Üretim Dashboard'a Dön
        </Button>
      </Space>
    </div>
  );
};

export default WorkflowManagement;