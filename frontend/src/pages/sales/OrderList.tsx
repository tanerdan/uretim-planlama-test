import React, { useState } from 'react';
import { 
  Table, 
  Card, 
  Button, 
  Space, 
  Tag, 
  Input, 
  Select, 
  DatePicker, 
  Row, 
  Col,
  Tooltip,
  Modal,
  message,
  Popconfirm
} from 'antd';
import { 
  PlusOutlined, 
  EyeOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { salesService } from '../../services/salesService';
import { Siparis } from '../../types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

const OrderList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Siparişleri getir
  const { 
    data: ordersData, 
    isLoading, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['orders', currentPage, pageSize, searchText, statusFilter],
    queryFn: () => salesService.getOrders({
      page: currentPage,
      limit: pageSize,
      search: searchText || undefined,
      durum: statusFilter
    }),
  });

  // Sipariş silme
  const deleteMutation = useMutation({
    mutationFn: salesService.deleteOrder,
    onSuccess: () => {
      message.success('Sipariş başarıyla silindi');
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
    onError: () => {
      message.error('Sipariş silinirken hata oluştu');
    },
  });

  const statusColors = {
    'beklemede': 'blue',
    'malzeme_planlandi': 'orange',
    'is_emirleri_olusturuldu': 'purple',
    'uretimde': 'green',
    'tamamlandi': 'success'
  };

  const statusLabels = {
    'beklemede': 'Beklemede',
    'malzeme_planlandi': 'Malzeme Planlandı',
    'is_emirleri_olusturuldu': 'İş Emirleri Oluşturuldu',
    'uretimde': 'Üretimde',
    'tamamlandi': 'Tamamlandı'
  };

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
      title: 'Teslim Tarihi',
      dataIndex: 'teslim_tarihi',
      key: 'teslim_tarihi',
      width: 120,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: 'Durum',
      dataIndex: 'durum',
      key: 'durum',
      width: 150,
      render: (durum: keyof typeof statusColors) => (
        <Tag color={statusColors[durum]} style={{ minWidth: '120px', textAlign: 'center' }}>
          {statusLabels[durum] || durum}
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
          <Tooltip title="Düzenle">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              size="small"
              onClick={() => navigate(`/sales/orders/${record.id}/edit`)}
            />
          </Tooltip>
          <Tooltip title="Sil">
            <Popconfirm
              title="Siparişi silmek istediğinizden emin misiniz?"
              onConfirm={() => deleteMutation.mutate(record.id)}
              okText="Evet"
              cancelText="Hayır"
            >
              <Button 
                type="text" 
                icon={<DeleteOutlined />} 
                size="small"
                danger
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

  const handleStatusFilter = (value: string) => {
    setStatusFilter(value === 'all' ? undefined : value);
    setCurrentPage(1);
  };

  const handleExport = () => {
    message.info('Excel export özelliği yakında eklenecek');
  };

  return (
    <div>
      {/* Filtreler */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="Sipariş no, müşteri ara..."
              allowClear
              onSearch={handleSearch}
              style={{ width: '100%' }}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Durum filtresi"
              style={{ width: '100%' }}
              allowClear
              onChange={handleStatusFilter}
              suffixIcon={<FilterOutlined />}
            >
              <Option value="all">Tümü</Option>
              <Option value="beklemede">Beklemede</Option>
              <Option value="malzeme_planlandi">Malzeme Planlandı</Option>
              <Option value="is_emirleri_olusturuldu">İş Emirleri Oluşturuldu</Option>
              <Option value="uretimde">Üretimde</Option>
              <Option value="tamamlandi">Tamamlandı</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={10}>
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => refetch()}
                loading={isLoading}
              >
                Yenile
              </Button>
              <Space>
                <Button
                  icon={<ExportOutlined />}
                  onClick={handleExport}
                >
                  Excel
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => navigate('/sales/orders/new')}
                >
                  Yeni Sipariş
                </Button>
              </Space>
            </Space>
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
          scroll={{ x: 1000 }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default OrderList;