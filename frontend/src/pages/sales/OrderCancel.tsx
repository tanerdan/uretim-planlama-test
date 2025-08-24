import React, { useState } from 'react';
import { 
  Table, 
  Card, 
  Button, 
  Space, 
  Tag, 
  Input, 
  Row, 
  Col,
  Tooltip,
  message,
  Popconfirm,
  Modal
} from 'antd';
import { 
  EyeOutlined, 
  StopOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { salesService } from '../../services/salesService';
import { Siparis } from '../../types';
import dayjs from 'dayjs';

const { Search } = Input;

const OrderCancel: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchText, setSearchText] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Sadece beklemede olan siparişleri getir
  const { 
    data: ordersData, 
    isLoading, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['pending-orders', currentPage, pageSize, searchText],
    queryFn: () => salesService.getOrders({
      page: currentPage,
      limit: pageSize,
      search: searchText || undefined,
      durum: 'beklemede' // Sadece beklemede olanlar
    }),
  });

  // Sipariş iptal etme
  const cancelMutation = useMutation({
    mutationFn: (orderId: number) => 
      salesService.updateOrderStatus(orderId, 'iptal'),
    onSuccess: () => {
      message.success('Sipariş başarıyla iptal edildi');
      queryClient.invalidateQueries({ queryKey: ['pending-orders'] });
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
    onError: () => {
      message.error('Sipariş iptal edilirken hata oluştu');
    },
  });

  const columns = [
    {
      title: 'Sipariş No',
      dataIndex: 'siparis_no',
      key: 'siparis_no',
      width: 120,
      render: (text: string, record: Siparis) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/sales/orders/${record.id}`)}
          style={{ padding: 0, fontWeight: 'bold' }}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'Müşteri',
      dataIndex: 'musteri_adi',
      key: 'musteri_adi',
      width: 200,
      render: (text: string, record: Siparis) => text || `Müşteri ID: ${record.musteri}`,
    },
    {
      title: 'Tarih',
      dataIndex: 'tarih',
      key: 'tarih',
      width: 120,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Durum',
      dataIndex: 'durum',
      key: 'durum',
      width: 120,
      render: () => (
        <Tag color="blue" style={{ minWidth: '100px', textAlign: 'center' }}>
          Beklemede
        </Tag>
      ),
    },
    {
      title: 'Toplam Tutar (USD)',
      dataIndex: 'toplam_tutar',
      key: 'toplam_tutar',
      width: 140,
      align: 'right' as const,
      render: (tutar: any) => {
        const amount = parseFloat(tutar) || 0;
        return `$${amount.toFixed(2)}`;
      },
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 120,
      render: (_, record: Siparis) => (
        <Space size="small">
          <Tooltip title="Detay Görüntüle">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              size="small"
              onClick={() => navigate(`/sales/orders/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="İptal Et">
            <Popconfirm
              title="Siparişi iptal etmek istediğinizden emin misiniz?"
              description="İptal edilen sipariş veritabanından silinmeyecek, sadece durumu 'İptal' olarak güncellenecektir."
              onConfirm={() => cancelMutation.mutate(record.id)}
              okText="Evet, İptal Et"
              cancelText="Hayır"
              okButtonProps={{ danger: true }}
            >
              <Button 
                type="text" 
                icon={<StopOutlined />} 
                size="small"
                danger
                loading={cancelMutation.isPending}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  const handleSearch = (value: string) => {
    setSearchText(value);
    setCurrentPage(1);
  };

  return (
    <div>
      {/* Filtreler */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={12}>
            <Search
              placeholder="Sipariş no, müşteri ara..."
              allowClear
              onSearch={handleSearch}
              style={{ width: '100%' }}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={12}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => refetch()}
                loading={isLoading}
              >
                Yenile
              </Button>
            </Space>
          </Col>
        </Row>
        <Row style={{ marginTop: '8px' }}>
          <Col span={24}>
            <Tag color="blue">
              Sadece "Beklemede" durumundaki siparişler gösterilmektedir
            </Tag>
          </Col>
        </Row>
      </Card>

      {/* Tablo */}
      <Card>
        <Table
          columns={columns}
          dataSource={ordersData?.results || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: ordersData?.count || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} / ${total} sipariş`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 10);
            },
          }}
          scroll={{ x: 800 }}
          size="small"
          locale={{
            emptyText: 'İptal edilebilir sipariş bulunmuyor'
          }}
        />
      </Card>
    </div>
  );
};

export default OrderCancel;