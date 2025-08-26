import React, { useState } from 'react';
import { Card, Table, Button, Space, Tag, Progress, Row, Col, Statistic, Typography, Divider, Modal, Form, Input, Select, InputNumber, message, App } from 'antd';
import { 
  ToolOutlined, 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import styled from 'styled-components';

const { Title } = Typography;

const PageHeader = styled.div`
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  color: white;
  padding: 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 8px 8px;
`;

const StationManagement: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const { modal } = App.useApp();
  
  // Modal states
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingStation, setEditingStation] = useState<any>(null);
  const [modalType, setModalType] = useState<'create' | 'edit'>('create');

  // Get stations data
  const { data: stations, isLoading: stationLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: productionService.getStations
  });

  // Mutations for CRUD operations
  const createMutation = useMutation({
    mutationFn: productionService.createStation,
    onSuccess: (newStation) => {
      queryClient.setQueryData(['stations'], (old: any[]) => {
        if (!old) return [newStation];
        // Replace temporary station with real one from server
        return [...old.filter(s => s.id !== 'temp'), newStation];
      });
      message.success('İstasyon başarıyla oluşturuldu');
      setIsModalVisible(false);
      form.resetFields();
    },
    onError: () => {
      message.error('İstasyon oluşturulurken hata oluştu');
      queryClient.invalidateQueries({ queryKey: ['stations'] });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => productionService.updateStation(id, data),
    onSuccess: (updatedStation) => {
      queryClient.setQueryData(['stations'], (old: any[]) => {
        if (!old) return [updatedStation];
        return old.map(station => 
          station.id === updatedStation.id ? updatedStation : station
        );
      });
      message.success('İstasyon başarıyla güncellendi');
      setIsModalVisible(false);
      form.resetFields();
      setEditingStation(null);
    },
    onError: () => {
      message.error('İstasyon güncellenirken hata oluştu');
      queryClient.invalidateQueries({ queryKey: ['stations'] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: productionService.deleteStation,
    onMutate: async (stationId: number) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['stations'] });
      
      // Snapshot the previous value
      const previousStations = queryClient.getQueryData(['stations']);
      
      // Optimistically update to the new value
      queryClient.setQueryData(['stations'], (old: any[]) => {
        if (!old) return [];
        return old.filter(station => station.id !== stationId);
      });
      
      // Return a context object with the snapshotted value
      return { previousStations };
    },
    onSuccess: () => {
      message.success('İstasyon başarıyla silindi');
    },
    onError: (error: any, stationId: number, context: any) => {
      console.error('Delete error:', error);
      
      // Rollback on error
      if (context?.previousStations) {
        queryClient.setQueryData(['stations'], context.previousStations);
      }
      
      let errorMessage = 'İstasyon silinirken hata oluştu';
      
      if (error?.response?.status === 400) {
        const data = error.response?.data;
        if (data?.detail) {
          errorMessage = data.detail;
        } else {
          errorMessage = 'Bu istasyon silinemez çünkü iş akışlarında kullanılıyor. Önce ilgili iş akışlarını düzenleyin.';
        }
      }
      
      message.error(errorMessage, 5); // 5 saniye göster
    },
    // Always refetch after error or success to ensure consistency
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['stations'] });
    }
  });

  // Transform data for display
  const stationData = (stations || []).map((station: any) => ({
    ...station,
    key: station.id,
    name: station.ad,
    code: station.kod,
    type: station.tip === 'makine' ? 'Makine' : 'El İşçiliği',
    status: station.durum?.toLowerCase() === 'aktif' ? 'active' : 
           station.durum?.toLowerCase() === 'bakım' ? 'maintenance' : 
           station.durum?.toLowerCase() === 'pasif' ? 'inactive' : 'active',
    lokasyon: station.lokasyon || 'Belirtilmemiş'
  }));

  // Handler functions
  const handleCreate = () => {
    setModalType('create');
    setEditingStation(null);
    setIsModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (station: any) => {
    setModalType('edit');
    setEditingStation(station);
    setIsModalVisible(true);
    form.setFieldsValue({
      ad: station.ad,
      kod: station.kod,
      tip: station.tip,
      durum: station.durum,
      gunluk_calisma_saati: station.gunluk_calisma_saati,
      gerekli_operator_sayisi: station.gerekli_operator_sayisi,
      saatlik_maliyet: station.saatlik_maliyet,
      lokasyon: station.lokasyon,
      aciklama: station.aciklama
    });
  };

  const handleDelete = (station: any) => {
    modal.confirm({
      title: 'İstasyonu Sil',
      content: (
        <div>
          <p>{station.name} istasyonunu silmek istediğinizden emin misiniz?</p>
          <p style={{ color: '#ff4d4f', marginTop: 8, fontSize: '12px' }}>
            ⚠️ Bu istasyon ile ilişkili iş akışları ve operasyonlar varsa silme işlemi başarısız olabilir.
          </p>
        </div>
      ),
      okText: 'Evet, Sil',
      cancelText: 'İptal',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(station.id);
      }
    });
  };

  const handleSubmit = (values: any) => {
    if (modalType === 'create') {
      createMutation.mutate(values);
    } else {
      updateMutation.mutate({ id: editingStation.id, data: values });
    }
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingStation(null);
    form.resetFields();
  };

  const columns = [
    {
      title: 'İstasyon Adı',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Kod',
      dataIndex: 'code',
      key: 'code',
      render: (code: string) => <Tag color="geekblue">{code}</Tag>
    },
    {
      title: 'Tip',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Günlük Çalışma',
      dataIndex: 'gunluk_calisma_saati',
      key: 'gunluk_calisma_saati',
      render: (hours: number) => `${hours || 0} saat/gün`
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          active: { color: 'success', text: 'Aktif', icon: <PlayCircleOutlined /> },
          maintenance: { color: 'warning', text: 'Bakım', icon: <SettingOutlined /> },
          inactive: { color: 'default', text: 'Pasif', icon: <PauseCircleOutlined /> }
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
      title: 'Gerekli Operatör',
      dataIndex: 'gerekli_operator_sayisi',
      key: 'gerekli_operator_sayisi',
      render: (count: number) => `${count || 0} kişi`
    },
    {
      title: 'Saatlik Maliyet',
      dataIndex: 'saatlik_maliyet',
      key: 'saatlik_maliyet',
      render: (cost: number) => cost > 0 ? `₺${cost}` : 'Belirlenmemiş'
    },
    {
      title: 'Lokasyon',
      dataIndex: 'lokasyon',
      key: 'lokasyon',
      render: (location: string) => location || 'Belirtilmemiş'
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (record: any) => (
        <Space>
          <Button 
            type="primary" 
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
            loading={deleteMutation.isPending}
          >
            Sil
          </Button>
        </Space>
      )
    }
  ];

  const totalStats = {
    totalStations: stationData.length,
    activeStations: stationData.filter(s => s.status === 'active').length,
    totalOperators: stationData.reduce((acc, s) => acc + (s.gerekli_operator_sayisi || 0), 0),
    totalWorkingHours: stationData.reduce((acc, s) => acc + (s.gunluk_calisma_saati || 0), 0),
    avgWorkingHours: stationData.length > 0 ? Math.round(stationData.reduce((acc, s) => acc + (s.gunluk_calisma_saati || 0), 0) / stationData.length) : 0
  };

  if (stationLoading) {
    return <div>İstasyon verileri yükleniyor...</div>;
  }

  return (
    <div>
      <PageHeader>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          <ToolOutlined style={{ marginRight: '12px' }} />
          İstasyon Yönetimi
        </Title>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
          Üretim istasyonlarını yönetin ve kapasitelerini takip edin
        </p>
      </PageHeader>

      {/* İstatistik Kartları */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Toplam İstasyon"
              value={totalStats.totalStations}
              prefix={<ToolOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Aktif İstasyon"
              value={totalStats.activeStations}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Toplam Operatör İhtiyacı"
              value={totalStats.totalOperators}
              prefix={<ToolOutlined />}
              suffix="kişi"
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Ortalama Çalışma Saati"
              value={totalStats.avgWorkingHours}
              suffix="saat/gün"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* İstasyon Tablosu */}
      <Card 
        title="İstasyon Listesi"
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleCreate}
            loading={createMutation.isPending}
          >
            Yeni İstasyon
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={stationData}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} / ${total} istasyon`
          }}
        />
      </Card>

      {/* İstasyon Ekleme/Düzenleme Modal */}
      <Modal
        title={modalType === 'create' ? 'Yeni İstasyon' : 'İstasyonu Düzenle'}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="İstasyon Adı"
                name="ad"
                rules={[{ required: true, message: 'İstasyon adı gereklidir' }]}
              >
                <Input placeholder="Örn: AG Sargı Makinesi" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="İstasyon Kodu"
                name="kod"
                rules={[{ required: true, message: 'İstasyon kodu gereklidir' }]}
              >
                <Input placeholder="Örn: AG-1" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Tip"
                name="tip"
                rules={[{ required: true, message: 'İstasyon tipi gereklidir' }]}
              >
                <Select placeholder="İstasyon tipini seçin">
                  <Select.Option value="makine">Makine</Select.Option>
                  <Select.Option value="el_iscilik">El İşçiliği</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Durum"
                name="durum"
                rules={[{ required: true, message: 'İstasyon durumu gereklidir' }]}
              >
                <Select placeholder="İstasyon durumunu seçin">
                  <Select.Option value="aktif">Aktif</Select.Option>
                  <Select.Option value="pasif">Pasif</Select.Option>
                  <Select.Option value="bakım">Bakım</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Günlük Çalışma Saati"
                name="gunluk_calisma_saati"
                rules={[{ required: true, message: 'Günlük çalışma saati gereklidir' }]}
              >
                <InputNumber
                  min={0}
                  max={24}
                  step={0.5}
                  placeholder="8.0"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Gerekli Operatör Sayısı"
                name="gerekli_operator_sayisi"
                rules={[{ required: true, message: 'Operatör sayısı gereklidir' }]}
              >
                <InputNumber
                  min={0}
                  placeholder="1"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Saatlik Maliyet (₺)"
                name="saatlik_maliyet"
              >
                <InputNumber
                  min={0}
                  step={0.01}
                  placeholder="0.00"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Lokasyon"
                name="lokasyon"
              >
                <Input placeholder="Örn: Atölye 1" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="Açıklama"
            name="aciklama"
          >
            <Input.TextArea 
              rows={3} 
              placeholder="İstasyon hakkında ek bilgiler..."
            />
          </Form.Item>

          <Form.Item style={{ textAlign: 'right', marginTop: 24 }}>
            <Space>
              <Button onClick={handleCancel}>
                İptal
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={modalType === 'create' ? createMutation.isPending : updateMutation.isPending}
              >
                {modalType === 'create' ? 'Oluştur' : 'Güncelle'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
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

export default StationManagement;