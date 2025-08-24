import React, { useState, useEffect } from 'react';
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
  Checkbox,
  Dropdown
} from 'antd';
import { 
  PlusOutlined, 
  EyeOutlined, 
  EditOutlined,
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  ReloadOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { salesService } from '../../services/salesService';
import { Siparis } from '../../types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

const OrderList: React.FC = () => {
  const navigate = useNavigate();
  
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [language, setLanguage] = useState<'tr' | 'en'>('tr');
  const [expandedRowKeys, setExpandedRowKeys] = useState<React.Key[]>([]);
  
  // Kolon görünürlük durumu
  const [visibleColumns, setVisibleColumns] = useState({
    siparis_no: true,
    musteri_adi: true,
    tarih: true,
    teslim_tarihi: true,
    durum: true,
    musteri_ulke: false,
    son_kullanici_ulke: true,
    toplam_tutar: true,
    olusturulma_tarihi: false,
    guncellenme_tarihi: false,
    notlar: false,
    actions: true
  });

  // Dil çevirileri
  const translations = {
    tr: {
      orderNo: 'Sipariş No',
      customer: 'Müşteri',
      date: 'Tarih',
      deliveryDate: 'Teslim Tarihi',
      status: 'Durum',
      customerCountry: 'Müşteri Ülke',
      endUserCountry: 'Son Kullanıcı Ülke',
      totalAmount: 'Toplam Tutar (USD)',
      createdDate: 'Oluşturulma Tarihi',
      updatedDate: 'Güncellenme Tarihi',
      notes: 'Notlar',
      actions: 'İşlemler',
      searchPlaceholder: 'Sipariş no, müşteri ara...',
      statusFilter: 'Durum filtresi',
      all: 'Tümü',
      refresh: 'Yenile',
      excel: 'Excel',
      newOrder: 'Yeni Sipariş',
      viewDetail: 'Detay Görüntüle',
      edit: 'Düzenle',
      orderTotal: 'sipariş',
      columnSettings: 'Kolon Ayarları',
      selectColumns: 'Kolonları Seç',
      orderItems: 'Sipariş Kalemleri',
      product: 'Ürün',
      quantity: 'Miktar',
      unitPrice: 'Birim Fiyat',
      currency: 'Para Birimi',
      totalPrice: 'Toplam',
      statusLabels: {
        'beklemede': 'Beklemede',
        'malzeme_planlandi': 'Malzeme Planlandı',
        'is_emirleri_olusturuldu': 'İş Emirleri Oluşturuldu',
        'uretimde': 'Üretimde',
        'tamamlandi': 'Tamamlandı',
        'iptal': 'İptal'
      }
    },
    en: {
      orderNo: 'Order No',
      customer: 'Customer',
      date: 'Date',
      deliveryDate: 'Delivery Date',
      status: 'Status',
      customerCountry: 'Customer Country',
      endUserCountry: 'End User Country',
      totalAmount: 'Total Amount (USD)',
      createdDate: 'Created Date',
      updatedDate: 'Updated Date',
      notes: 'Notes',
      actions: 'Actions',
      searchPlaceholder: 'Search order no, customer...',
      statusFilter: 'Status filter',
      all: 'All',
      refresh: 'Refresh',
      excel: 'Excel',
      newOrder: 'New Order',
      viewDetail: 'View Detail',
      edit: 'Edit',
      orderTotal: 'orders',
      columnSettings: 'Column Settings',
      selectColumns: 'Select Columns',
      orderItems: 'Order Items',
      product: 'Product',
      quantity: 'Quantity',
      unitPrice: 'Unit Price',
      currency: 'Currency',
      totalPrice: 'Total',
      statusLabels: {
        'beklemede': 'Pending',
        'malzeme_planlandi': 'Materials Planned',
        'is_emirleri_olusturuldu': 'Work Orders Created',
        'uretimde': 'In Production',
        'tamamlandi': 'Completed',
        'iptal': 'Cancelled'
      }
    }
  };

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

  const statusColors = {
    'beklemede': 'blue',
    'malzeme_planlandi': 'orange',
    'is_emirleri_olusturuldu': 'purple',
    'uretimde': 'green',
    'tamamlandi': 'success',
    'iptal': 'error'
  };

  const t = translations[language];

  // Local storage'dan kolon ayarlarını yükle
  useEffect(() => {
    const defaultColumns = {
      siparis_no: true,
      musteri_adi: true,
      tarih: true,
      teslim_tarihi: true,
      durum: true,
      musteri_ulke: false,
      son_kullanici_ulke: true,
      toplam_tutar: true,
      olusturulma_tarihi: false,
      guncellenme_tarihi: false,
      notlar: false,
      actions: true
    };

    const savedColumns = localStorage.getItem('orderList_visibleColumns');
    if (savedColumns) {
      const parsedColumns = JSON.parse(savedColumns);
      // Yeni kolonları default değerlerle birleştir
      const mergedColumns = { ...defaultColumns, ...parsedColumns };
      setVisibleColumns(mergedColumns);
    } else {
      setVisibleColumns(defaultColumns);
    }
  }, []);

  // Kolon ayarlarını local storage'a kaydet
  const saveColumnSettings = (newVisibleColumns: typeof visibleColumns) => {
    setVisibleColumns(newVisibleColumns);
    localStorage.setItem('orderList_visibleColumns', JSON.stringify(newVisibleColumns));
  };

  // Kolon toggle fonksiyonu
  const toggleColumn = (columnKey: string) => {
    const currentValue = visibleColumns[columnKey as keyof typeof visibleColumns];
    const newValue = currentValue !== undefined ? !currentValue : true;
    const newVisibleColumns = {
      ...visibleColumns,
      [columnKey]: newValue
    };
    saveColumnSettings(newVisibleColumns);
  };

  const allColumns = [
    {
      title: t.orderNo,
      dataIndex: 'siparis_no',
      key: 'siparis_no',
      width: 120,
      render: (text: string) => (
        <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
          {text}
        </span>
      ),
    },
    {
      title: t.customer,
      dataIndex: 'musteri_adi',
      key: 'musteri_adi',
      width: 200,
      render: (text: string, record: Siparis) => text || `${language === 'tr' ? 'Müşteri ID' : 'Customer ID'}: ${record.musteri}`,
    },
    {
      title: t.date,
      dataIndex: 'tarih',
      key: 'tarih',
      width: 120,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: t.deliveryDate,
      dataIndex: 'teslim_tarihi',
      key: 'teslim_tarihi',
      width: 120,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
    },
    {
      title: t.status,
      dataIndex: 'durum',
      key: 'durum',
      width: 150,
      render: (durum: keyof typeof statusColors) => (
        <Tag color={statusColors[durum]} style={{ minWidth: '120px', textAlign: 'center' }}>
          {t.statusLabels[durum] || durum}
        </Tag>
      ),
    },
    {
      title: t.totalAmount,
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
      title: t.customerCountry,
      dataIndex: 'musteri_ulke',
      key: 'musteri_ulke',
      width: 120,
      render: (country: string) => country || '-',
    },
    {
      title: t.endUserCountry,
      dataIndex: 'son_kullanici_ulke',
      key: 'son_kullanici_ulke',
      width: 140,
      render: (country: string, record: Siparis) => {
        // Kalemlerden son kullanıcı ülkeleri topla
        if (record.kalemler && record.kalemler.length > 0) {
          const countries = record.kalemler
            .map(kalem => kalem.son_kullanici_ulke)
            .filter(ulke => ulke && ulke !== '') // Boş olanları filtrele
            .filter((ulke, index, arr) => arr.indexOf(ulke) === index); // Tekrarları kaldır
          
          if (countries.length > 0) {
            const displayText = countries.join(', ');
            // Çok uzunsa tooltip ile göster
            if (displayText.length > 15) {
              return (
                <Tooltip title={displayText}>
                  <span style={{ cursor: 'help' }}>
                    {countries.length > 1 
                      ? `${countries[0]} +${countries.length - 1}` 
                      : displayText
                    }
                  </span>
                </Tooltip>
              );
            }
            return displayText;
          }
        }
        
        // Kalem yoksa veya kalem ülkeleri boşsa sipariş seviyesindeki değeri kullan
        return country || '-';
      },
    },
    {
      title: t.createdDate,
      dataIndex: 'olusturulma_tarihi',
      key: 'olusturulma_tarihi',
      width: 140,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: t.updatedDate,
      dataIndex: 'guncellenme_tarihi',
      key: 'guncellenme_tarihi',
      width: 140,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: t.notes,
      dataIndex: 'notlar',
      key: 'notlar',
      width: 200,
      render: (notes: string) => (
        <div style={{ 
          maxWidth: '180px', 
          whiteSpace: 'nowrap', 
          overflow: 'hidden', 
          textOverflow: 'ellipsis' 
        }}>
          {notes || '-'}
        </div>
      ),
    },
    {
      title: t.actions,
      key: 'actions',
      width: 120,
      render: (_: any, record: Siparis) => (
        <Space size="small">
          <Tooltip title={t.viewDetail}>
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              size="small"
              onClick={() => navigate(`/sales/orders/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title={t.edit}>
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              size="small"
              onClick={() => navigate(`/sales/orders/${record.id}/edit`)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Görünür kolonları filtrele
  const columns = allColumns.filter((column) => {
    const key = column.key as keyof typeof visibleColumns;
    return visibleColumns[key] === true;
  });

  // Kolon seçici dropdown menüsü
  const columnSelectorMenu = (
    <div style={{ padding: '8px', minWidth: '200px' }}>
      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>{t.selectColumns}</div>
      {allColumns.map((column) => {
        const key = column.key as keyof typeof visibleColumns;
        const visible = visibleColumns[key] !== undefined ? visibleColumns[key] : false;
        return (
          <div key={key} style={{ marginBottom: '4px' }}>
            <Checkbox
              checked={visible}
              onChange={() => toggleColumn(key)}
            >
              {column.title}
            </Checkbox>
          </div>
        );
      })}
    </div>
  );

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

  // Sipariş kalemlerini görüntüleyen expand component
  const expandedRowRender = (record: Siparis) => {
    const items = record.kalemler || [];
    
    if (items.length === 0) {
      return <div style={{ padding: '16px', color: '#666' }}>Bu siparişte kalem bulunmuyor.</div>;
    }

    const itemColumns = [
      {
        title: t.product,
        dataIndex: 'urun_adi',
        key: 'urun_adi',
        render: (text: string, item: any) => text || `Ürün ID: ${item.urun}`,
      },
      {
        title: t.quantity,
        dataIndex: 'miktar',
        key: 'miktar',
        width: 80,
        align: 'center' as const,
      },
      {
        title: t.unitPrice,
        dataIndex: 'birim_fiyat',
        key: 'birim_fiyat',
        width: 100,
        align: 'right' as const,
        render: (price: any, item: any) => {
          const numPrice = parseFloat(price) || 0;
          return `${numPrice.toFixed(2)} ${item.doviz || 'USD'}`;
        },
      },
      {
        title: `${t.unitPrice} (USD)`,
        dataIndex: 'birim_fiyat_usd',
        key: 'birim_fiyat_usd',
        width: 120,
        align: 'right' as const,
        render: (price: any) => {
          const numPrice = parseFloat(price) || 0;
          return `$${numPrice.toFixed(2)}`;
        },
      },
      {
        title: t.totalPrice,
        dataIndex: 'toplam_tutar',
        key: 'toplam_tutar',
        width: 120,
        align: 'right' as const,
        render: (total: any) => {
          const numTotal = parseFloat(total) || 0;
          return (
            <strong style={{ color: '#1890ff' }}>
              ${numTotal.toFixed(2)}
            </strong>
          );
        },
      },
      {
        title: t.deliveryDate,
        dataIndex: 'teslim_tarihi',
        key: 'teslim_tarihi',
        width: 120,
        render: (date: string) => dayjs(date).format('DD.MM.YYYY'),
      },
      {
        title: t.endUserCountry,
        dataIndex: 'son_kullanici_ulke',
        key: 'son_kullanici_ulke',
        width: 120,
        render: (country: string) => country || '-',
      },
    ];

    return (
      <div style={{ margin: '8px 0' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#1890ff' }}>{t.orderItems}</h4>
        <Table
          columns={itemColumns}
          dataSource={items}
          pagination={false}
          size="small"
          rowKey="id"
          style={{ backgroundColor: '#fafafa' }}
        />
      </div>
    );
  };

  return (
    <div>
      {/* Filtreler */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8} md={6}>
            <Search
              placeholder={t.searchPlaceholder}
              allowClear
              onSearch={handleSearch}
              style={{ width: '100%' }}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={8} md={5}>
            <Select
              placeholder={t.statusFilter}
              style={{ width: '100%' }}
              allowClear
              onChange={handleStatusFilter}
              suffixIcon={<FilterOutlined />}
            >
              <Option value="all">{t.all}</Option>
              <Option value="beklemede">{t.statusLabels.beklemede}</Option>
              <Option value="malzeme_planlandi">{t.statusLabels.malzeme_planlandi}</Option>
              <Option value="is_emirleri_olusturuldu">{t.statusLabels.is_emirleri_olusturuldu}</Option>
              <Option value="uretimde">{t.statusLabels.uretimde}</Option>
              <Option value="tamamlandi">{t.statusLabels.tamamlandi}</Option>
              <Option value="iptal">{t.statusLabels.iptal}</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={3}>
            <Select
              value={language}
              onChange={setLanguage}
              style={{ width: '100%' }}
            >
              <Option value="tr">🇹🇷 TR</Option>
              <Option value="en">🇺🇸 EN</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={10}>
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => refetch()}
                loading={isLoading}
              >
                {t.refresh}
              </Button>
              <Space>
                <Dropdown 
                  popupRender={() => columnSelectorMenu} 
                  trigger={['click']}
                  placement="bottomRight"
                >
                  <Button icon={<SettingOutlined />}>
                    {t.columnSettings}
                  </Button>
                </Dropdown>
                <Button
                  icon={<ExportOutlined />}
                  onClick={handleExport}
                >
                  {t.excel}
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => navigate('/sales/orders/new')}
                >
                  {t.newOrder}
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
          expandable={{
            expandedRowRender,
            expandedRowKeys,
            onExpandedRowsChange: (expandedRows: readonly React.Key[]) => setExpandedRowKeys([...expandedRows]),
            expandRowByClick: true,
            rowExpandable: (record: Siparis) => Boolean(record.kalemler && record.kalemler.length > 0),
          }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: ordersData?.count || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} / ${total} ${t.orderTotal}`,
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