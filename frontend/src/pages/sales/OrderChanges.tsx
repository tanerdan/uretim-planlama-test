import React, { useState } from 'react';
import { 
  Table, 
  Card, 
  Button, 
  Space, 
  Tag, 
  Input, 
  Select, 
  Row, 
  Col,
  Tooltip,
} from 'antd';
import { 
  EditOutlined, 
  SearchOutlined,
  FilterOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { salesService } from '../../services/salesService';
import { Siparis } from '../../types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;

const OrderChanges: React.FC = () => {
  const navigate = useNavigate();
  
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
    queryKey: ['orders-changes', currentPage, pageSize, searchText, statusFilter],
    queryFn: () => salesService.getOrders({
      page: currentPage,
      limit: pageSize,
      search: searchText || undefined,
      durum: statusFilter
    }),
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

  const handleEditOrder = (orderId: number) => {
    navigate(`/sales/orders/${orderId}/edit`);
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
          onClick={() => handleEditOrder(record.id)}
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
      title: 'Müşteri Ülke',
      dataIndex: 'musteri_ulke',
      key: 'musteri_ulke',
      width: 100,
    },
    {
      title: 'Son Güncelleme',
      dataIndex: 'guncellenme_tarihi',
      key: 'guncellenme_tarihi',
      width: 150,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 100,
      render: (_: any, record: Siparis) => (
        <Space size="small">
          <Tooltip title="Siparişi Düzenle">
            <Button 
              type="primary" 
              icon={<EditOutlined />} 
              size="small"
              onClick={() => handleEditOrder(record.id)}
            >
              Düzenle
            </Button>
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

  return (
    <div>
      {/* Başlık */}
      <Card style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <h2 style={{ margin: 0 }}>Sipariş Değişiklikleri</h2>
            <p style={{ margin: '4px 0 0 0', color: '#666' }}>
              Mevcut siparişleri düzenlemek için sipariş numarasına veya düzenle butonuna tıklayın.
            </p>
          </Col>
        </Row>
      </Card>

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
          scroll={{ x: 1100 }}
          size="small"
          onRow={(record) => ({
            style: { cursor: 'pointer' },
            onClick: (e) => {
              // Sadece satıra tıklandığında, butona değil
              if ((e.target as HTMLElement).closest('button')) return;
              handleEditOrder(record.id);
            },
          })}
        />
      </Card>
    </div>
  );
};

export default OrderChanges;