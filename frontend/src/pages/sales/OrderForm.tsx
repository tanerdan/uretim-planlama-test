import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Select, 
  DatePicker, 
  Button, 
  Space, 
  Divider,
  Table,
  InputNumber,
  message,
  Row,
  Col,
  Typography,
  Upload
} from 'antd';
import { 
  PlusOutlined, 
  MinusCircleOutlined, 
  SaveOutlined,
  ArrowLeftOutlined,
  SyncOutlined,
  UploadOutlined,
  InboxOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesService } from '../../services/salesService';
import { Musteri, Urun, Siparis, SiparisKalem, Ulke } from '../../types';
import dayjs from 'dayjs';
import styled from 'styled-components';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const StyledCard = styled(Card)`
  .ant-card-head {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    .ant-card-head-title {
      color: white;
      font-weight: bold;
    }
  }
`;

const OrderItemsTable = styled.div`
  .ant-table-thead > tr > th {
    background: #f5f5f5;
    font-weight: bold;
  }
`;

interface OrderFormData {
  musteri: number;
  siparis_no: string;
  tarih: string;
  musteri_ulke: string;
  son_kullanici_ulke: string;
  aciklama?: string;
  kalemler: {
    urun: number;
    miktar: number;
    birim_fiyat: number;
    doviz: string;
    kur: number;
    birim_fiyat_usd: number;
    teslim_tarihi: string;
    son_kullanici_ulke: string;
    notlar?: string;
  }[];
}

const OrderForm: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const isEdit = Boolean(id);

  // State
  const [orderItems, setOrderItems] = useState<SiparisKalem[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<number | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isProductSyncing, setIsProductSyncing] = useState(false);
  const [customerCountry, setCustomerCountry] = useState<string>('TR');
  const [endUserCountry, setEndUserCountry] = useState<string>('TR');
  
  // Kur state'leri
  const [currencies, setCurrencies] = useState<any[]>([]);
  const [exchangeRates, setExchangeRates] = useState<any>({});
  
  // Dosya state'leri
  const [siparisMetkubu, setSiparisMetkubu] = useState<any[]>([]);
  const [maliyetHesabi, setMaliyetHesabi] = useState<any[]>([]);
  const [ekDosyalar, setEkDosyalar] = useState<any[]>([]);

  // API calls
  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => salesService.getCustomers({ page: 1, limit: 1000 }),
  });

  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: () => salesService.getProducts({ page: 1, limit: 1000 }),
  });

  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: () => salesService.getCountries(),
  });

  // Kur bilgileri
  const { data: currenciesData } = useQuery({
    queryKey: ['currencies'],
    queryFn: () => salesService.getCurrencies(),
  });

  const { data: ratesData } = useQuery({
    queryKey: ['exchange-rates'],
    queryFn: () => salesService.getExchangeRates('USD'),
    refetchInterval: 300000, // 5 dakikada bir güncelle
  });

  // Update state when data changes
  useEffect(() => {
    if (currenciesData?.data) {
      setCurrencies(currenciesData.data);
    }
  }, [currenciesData]);

  useEffect(() => {
    if (ratesData?.rates) {
      setExchangeRates(ratesData.rates);
    }
  }, [ratesData]);

  const { data: orderData, isLoading: orderLoading } = useQuery({
    queryKey: ['order', id],
    queryFn: () => salesService.getOrderById(Number(id)),
    enabled: isEdit,
  });

  // Create/Update mutations
  const createMutation = useMutation({
    mutationFn: salesService.createOrder,
    onSuccess: async (newOrder: Siparis) => {
      
      // Sipariş oluşturulduktan sonra dosyaları yükle
      const uploadPromises = [];
      
      // Sipariş mektubu yükle
      if (siparisMetkubu.length > 0) {
        if (siparisMetkubu[0].originFileObj) {
          uploadPromises.push(
            salesService.uploadOrderFile(newOrder.id, siparisMetkubu[0].originFileObj, 'Sipariş Mektubu')
          );
        }
      }
      
      // Maliyet hesabı yükle
      if (maliyetHesabi.length > 0) {
        uploadPromises.push(
          salesService.uploadOrderFile(newOrder.id, maliyetHesabi[0].originFileObj, 'Maliyet Hesabı')
        );
      }
      
      // Ek dosyaları yükle
      if (ekDosyalar.length > 0) {
        for (const file of ekDosyalar) {
          uploadPromises.push(
            salesService.uploadOrderFile(newOrder.id, file.originFileObj, 'Ek Dosya')
          );
        }
      }
      
      // Tüm dosyalar yüklendiğinde
      if (uploadPromises.length > 0) {
        try {
          await Promise.all(uploadPromises);
          message.success(`Sipariş ve ${uploadPromises.length} dosya başarıyla yüklendi`);
        } catch (error) {
          console.error('File upload error:', error);
          message.warning('Sipariş oluşturuldu ancak bazı dosyalar yüklenemedi');
        }
      } else {
        message.success('Sipariş başarıyla oluşturuldu');
      }
      
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      navigate('/sales/orders');
    },
    onError: () => {
      message.error('Sipariş oluşturulurken hata oluştu');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Siparis> }) => 
      salesService.updateOrder(id, data),
    onSuccess: () => {
      message.success('Sipariş başarıyla güncellendi');
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      navigate('/sales/orders');
    },
    onError: () => {
      message.error('Sipariş güncellenirken hata oluştu');
    },
  });

  // Form initialization for edit mode
  useEffect(() => {
    if (isEdit && orderData) {
      const customerCountryValue = orderData.musteri_ulke || 'TR';
      const endUserCountryValue = orderData.son_kullanici_ulke || customerCountryValue;
      
      form.setFieldsValue({
        musteri: orderData.musteri,
        siparis_no: orderData.siparis_no,
        tarih: dayjs(orderData.tarih),
        musteri_ulke: customerCountryValue,
        son_kullanici_ulke: endUserCountryValue,
      });
      
      setSelectedCustomer(orderData.musteri);
      setCustomerCountry(customerCountryValue);
      setEndUserCountry(endUserCountryValue);
      
      if (orderData.kalemler) {
        setOrderItems(orderData.kalemler);
      }
    }
  }, [isEdit, orderData, form]);

  // Generate order number for new orders
  useEffect(() => {
    if (!isEdit) {
      const timestamp = Date.now().toString().slice(-6); // Son 6 hane
      const orderNo = `SIP-${dayjs().format('YYYY')}-${timestamp}`;
      form.setFieldValue('siparis_no', orderNo);
    }
  }, [isEdit, form]);

  const addOrderItem = () => {
    const newItem: SiparisKalem = {
      id: Date.now(), // Temporary ID for new items
      siparis: Number(id) || 0,
      urun: 0,
      miktar: 1,
      birim_fiyat: 0,
      doviz: 'USD',
      kur: 1.0,
      birim_fiyat_usd: 0,
      teslim_tarihi: dayjs().add(7, 'days').format('YYYY-MM-DD'),
      son_kullanici_ulke: endUserCountry,
      toplam_tutar: 0,
      olusturulma_tarihi: new Date().toISOString(),
      notlar: '',
    };
    setOrderItems([...orderItems, newItem]);
  };

  const removeOrderItem = (index: number) => {
    const newItems = orderItems.filter((_, i) => i !== index);
    setOrderItems(newItems);
  };

  const updateOrderItem = (index: number, field: keyof SiparisKalem, value: any) => {
    const newItems = [...orderItems];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // Kur değişikliğinde USD fiyatını güncelle
    if (field === 'doviz') {
      const selectedCurrency = value;
      const rate = exchangeRates[selectedCurrency];
      
      if (rate && selectedCurrency !== 'USD') {
        newItems[index].kur = 1 / rate; // 1 selected_currency = X USD
      } else if (selectedCurrency === 'USD') {
        newItems[index].kur = 1;
      } else {
        // Fallback kurlar
        const fallbackRates = {
          'EUR': 0.85,
          'GBP': 0.73,
          'TRY': 27.50,
          'JPY': 110.0,
          'CHF': 0.92,
          'CAD': 1.25,
          'AUD': 1.45
        };
        newItems[index].kur = 1 / (fallbackRates[selectedCurrency as keyof typeof fallbackRates] || 1);
      }
      
      newItems[index].birim_fiyat_usd = newItems[index].birim_fiyat * newItems[index].kur;
    }
    
    // Fiyat değişikliğinde USD fiyatını güncelle
    if (field === 'birim_fiyat' || field === 'kur') {
      newItems[index].birim_fiyat_usd = newItems[index].birim_fiyat * (newItems[index].kur || 1);
    }
    
    // Calculate total for the item (USD cinsinden)
    if (field === 'miktar' || field === 'birim_fiyat' || field === 'doviz' || field === 'kur') {
      newItems[index].toplam_tutar = newItems[index].miktar * newItems[index].birim_fiyat_usd;
    }
    
    setOrderItems(newItems);
  };

  const calculateTotal = () => {
    return orderItems.reduce((sum, item) => {
      const tutar = parseFloat(item.toplam_tutar as any) || 0;
      return sum + tutar;
    }, 0);
  };

  // Manuel kur girişi için fonksiyon
  const updateManualRate = (index: number, manualRate: number) => {
    const newItems = [...orderItems];
    newItems[index].kur = manualRate;
    newItems[index].birim_fiyat_usd = newItems[index].birim_fiyat * manualRate;
    newItems[index].toplam_tutar = newItems[index].miktar * newItems[index].birim_fiyat_usd;
    setOrderItems(newItems);
  };

  // Müşteri senkronizasyonu
  const handleCustomerSync = async () => {
    setIsSyncing(true);
    try {
      await salesService.syncCustomersFromMikroFly();
      message.success('Müşteri bilgileri Mikro Fly V17\'den başarıyla senkronize edildi');
      // Müşteri listesini yenile
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    } catch (error) {
      message.error('Senkronizasyon sırasında hata oluştu. Mikro Fly bağlantısını kontrol edin.');
    } finally {
      setIsSyncing(false);
    }
  };

  // Ürün senkronizasyonu
  const handleProductSync = async () => {
    setIsProductSyncing(true);
    try {
      const result = await salesService.syncProductsFromMikroFly();
      message.success(`${result.synchronized_count} ürün Mikro Fly V17'den başarıyla senkronize edildi (${result.new_count} yeni, ${result.updated_count} güncellendi)`);
      // Ürün listesini yenile
      queryClient.invalidateQueries({ queryKey: ['products'] });
    } catch (error) {
      message.error('Ürün senkronizasyonu sırasında hata oluştu. Mikro Fly bağlantısını kontrol edin.');
    } finally {
      setIsProductSyncing(false);
    }
  };

  const handleCustomerChange = (customerId: number) => {
    setSelectedCustomer(customerId);
    const customer = customers?.results?.find(c => c.id === customerId);
    if (customer && customer.ulke) {
      setCustomerCountry(customer.ulke);
      setEndUserCountry(customer.ulke); // Default olarak müşteri ülkesi ile aynı
      form.setFieldsValue({
        musteri_ulke: customer.ulke,
        son_kullanici_ulke: customer.ulke
      });
    }
  };

  const handleEndUserCountryChange = (country: string) => {
    setEndUserCountry(country);
    form.setFieldValue('son_kullanici_ulke', country);
  };

  const onFinish = (values: any) => {
    // Zorunlu alan kontrolleri
    if (orderItems.length === 0) {
      message.error('En az bir sipariş kalemi eklemelisiniz');
      return;
    }
    
    // JSON formatında veri hazırla
    const orderData = {
      siparis_no: values.siparis_no,
      musteri: values.musteri,
      tarih: values.tarih.format('YYYY-MM-DD'),
      musteri_ulke: values.musteri_ulke,
      son_kullanici_ulke: values.son_kullanici_ulke || values.musteri_ulke,
      durum: isEdit ? undefined : 'beklemede' as const,
      notlar: values.aciklama || '',
      kalemler: JSON.stringify(orderItems.map(item => ({
        urun: item.urun,
        miktar: item.miktar,
        birim_fiyat: item.birim_fiyat,
        doviz: item.doviz || 'USD',
        kur: item.kur || 1,
        birim_fiyat_usd: item.birim_fiyat_usd || 0,
        teslim_tarihi: item.teslim_tarihi || dayjs().add(7, 'days').format('YYYY-MM-DD'),
        son_kullanici_ulke: item.son_kullanici_ulke || values.son_kullanici_ulke || values.musteri_ulke || 'TR',
        notlar: item.notlar || '',
      })))
    };

    if (isEdit && id) {
      updateMutation.mutate({ id: Number(id), data: orderData });
    } else {
      // Yeni sipariş oluştur
      createMutation.mutate(orderData);
    }
  };

  const orderItemColumns = [
    {
      title: (
        <Space>
          Ürün
          <Button
            type="link"
            size="small"
            icon={<SyncOutlined spin={isProductSyncing} />}
            onClick={handleProductSync}
            loading={isProductSyncing}
            title="Mikro Fly V17'den ürün bilgilerini senkronize et"
            style={{ padding: 0, height: 'auto' }}
          >
            {isProductSyncing ? 'Senkronize ediliyor...' : 'Mikro Fly\'den Senkronize Et'}
          </Button>
        </Space>
      ),
      dataIndex: 'urun',
      key: 'urun',
      width: '20%',
      render: (value: number, record: SiparisKalem, index: number) => (
        <Select
          placeholder="Ürün seçin"
          value={value || undefined}
          onChange={(val) => updateOrderItem(index, 'urun', val)}
          style={{ width: '100%' }}
          showSearch
          optionFilterProp="children"
        >
          {products?.results?.map((product: Urun) => (
            <Option key={product.id} value={product.id}>
              {`${product.ad} - ${product.kod}`}
            </Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Miktar',
      dataIndex: 'miktar',
      key: 'miktar',
      width: '8%',
      render: (value: number, record: SiparisKalem, index: number) => (
        <InputNumber
          min={1}
          value={value}
          onChange={(val) => updateOrderItem(index, 'miktar', val || 1)}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: 'Fiyat / Para Birimi',
      dataIndex: 'birim_fiyat',
      key: 'birim_fiyat',
      width: '16%',
      render: (value: number, record: SiparisKalem, index: number) => (
        <div style={{ display: 'flex', gap: '4px' }}>
          <InputNumber
            min={0}
            precision={2}
            value={value}
            onChange={(val) => updateOrderItem(index, 'birim_fiyat', val || 0)}
            style={{ width: '120px' }}
            placeholder="Fiyat"
          />
          <Select
            value={record.doviz || 'USD'}
            onChange={(val) => updateOrderItem(index, 'doviz', val)}
            style={{ width: '65px' }}
            size="small"
          >
            <Option value="USD">USD</Option>
            <Option value="EUR">EUR</Option>
            <Option value="GBP">GBP</Option>
            <Option value="TRY">TRY</Option>
            <Option value="JPY">JPY</Option>
            <Option value="CHF">CHF</Option>
            <Option value="CAD">CAD</Option>
            <Option value="AUD">AUD</Option>
          </Select>
        </div>
      ),
    },
    {
      title: 'USD Fiyat / Kur',
      key: 'usd_price',
      width: '13%',
      render: (record: SiparisKalem, _: any, index: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 'bold', color: '#1890ff', fontSize: '14px' }}>
              ${(parseFloat(record.birim_fiyat_usd as any) || 0).toFixed(2)}
            </span>
            <InputNumber
              size="small"
              min={0}
              precision={4}
              value={record.kur || 1}
              onChange={(val) => updateManualRate(index, val || 1)}
              style={{ width: '80px' }}
              controls={false}
              placeholder="Kur"
            />
          </div>
        </div>
      ),
    },
    {
      title: 'Teslim Tarihi',
      dataIndex: 'teslim_tarihi',
      key: 'teslim_tarihi',
      width: '9%',
      render: (value: string, record: SiparisKalem, index: number) => (
        <DatePicker
          value={value ? dayjs(value) : dayjs().add(7, 'days')}
          onChange={(date) => updateOrderItem(index, 'teslim_tarihi', date?.format('YYYY-MM-DD') || '')}
          style={{ width: '100%' }}
          format="DD.MM.YYYY"
          placeholder="Teslim tarihi"
        />
      ),
    },
    {
      title: 'Son Kullanıcı Ülke',
      dataIndex: 'son_kullanici_ulke',
      key: 'son_kullanici_ulke',
      width: '9%',
      render: (value: string, record: SiparisKalem, index: number) => (
        <Select
          value={record.son_kullanici_ulke || value || 'TR'}
          onChange={(val) => updateOrderItem(index, 'son_kullanici_ulke', val)}
          style={{ width: '100%' }}
          showSearch
          placeholder="Ülke seçin"
          optionFilterProp="children"
        >
          {countries?.map((country: Ulke) => (
            <Option key={country.kod} value={country.kod}>
              {country.ad}
            </Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Toplam (USD)',
      dataIndex: 'toplam_tutar',
      key: 'toplam_tutar',
      width: '8%',
      render: (value: number) => (
        <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
          ${(parseFloat(value as any) || 0).toFixed(2)}
        </span>
      ),
    },
    {
      title: 'Açıklama',
      dataIndex: 'notlar',
      key: 'notlar',
      width: '28%',
      render: (value: string, record: SiparisKalem, index: number) => (
        <Input.TextArea
          rows={1}
          value={value}
          onChange={(e) => updateOrderItem(index, 'notlar', e.target.value)}
          placeholder="Açıklama (opsiyonel)"
        />
      ),
    },
    {
      title: 'İşlem',
      key: 'action',
      width: '5%',
      render: (_: any, record: SiparisKalem, index: number) => (
        <Button
          type="text"
          danger
          icon={<MinusCircleOutlined />}
          onClick={() => removeOrderItem(index)}
          size="small"
        />
      ),
    },
  ];

  if (orderLoading) {
    return <Card loading />;
  }

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/sales/orders')}>
          Geri
        </Button>
        <Title level={3} style={{ margin: 0 }}>
          {isEdit ? 'Sipariş Düzenle' : 'Yeni Sipariş'}
        </Title>
      </Space>

      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          tarih: dayjs(),
          musteri_ulke: 'TR',
          son_kullanici_ulke: 'TR',
        }}
      >
        <StyledCard title="Sipariş Bilgileri">
          <Row gutter={16}>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                name="siparis_no"
                label="Sipariş No"
                rules={[{ required: true, message: 'Sipariş no gerekli' }]}
              >
                <Input placeholder="SIP-2025-001" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={10}>
              <Form.Item
                name="musteri"
                label={
                  <Space>
                    Müşteri
                    <Button
                      type="link"
                      size="small"
                      icon={<SyncOutlined spin={isSyncing} />}
                      onClick={handleCustomerSync}
                      loading={isSyncing}
                      title="Mikro Fly V17'den müşteri bilgilerini senkronize et"
                      style={{ padding: 0, height: 'auto' }}
                    >
                      {isSyncing ? 'Senkronize ediliyor...' : 'Mikro Fly\'den Senkronize Et'}
                    </Button>
                  </Space>
                }
                rules={[{ required: true, message: 'Müşteri seçimi gerekli' }]}
              >
                <Select
                  placeholder="Müşteri seçin"
                  showSearch
                  filterOption={(input, option) =>
                    String(option?.children || '')?.toLowerCase().includes(input.toLowerCase())
                  }
                  onChange={handleCustomerChange}
                >
                  {customers?.results?.map((customer: Musteri) => (
                    <Option key={customer.id} value={customer.id}>
                      {customer.ad}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Form.Item
                name="tarih"
                label="Sipariş Tarihi"
                rules={[{ required: true, message: 'Sipariş tarihi gerekli' }]}
              >
                <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={12} md={6}>
              <Form.Item
                name="musteri_ulke"
                label="Müşteri Ülke"
                rules={[{ required: true, message: 'Müşteri ülkesi gerekli' }]}
              >
                <Select
                  placeholder="Ülke seçin"
                  showSearch
                  filterOption={(input, option) =>
                    String(option?.children || '')?.toLowerCase().includes(input.toLowerCase())
                  }
                  value={customerCountry}
                  onChange={(value) => setCustomerCountry(value)}
                >
                  {countries?.map((country: Ulke) => (
                    <Option key={country.kod} value={country.kod}>
                      {country.ad}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Form.Item
                name="son_kullanici_ulke"
                label="Son Kullanıcı Ülke"
                rules={[{ required: true, message: 'Son kullanıcı ülkesi gerekli' }]}
              >
                <Select
                  placeholder="Ülke seçin"
                  showSearch
                  filterOption={(input, option) =>
                    String(option?.children || '')?.toLowerCase().includes(input.toLowerCase())
                  }
                  value={endUserCountry}
                  onChange={handleEndUserCountryChange}
                >
                  {countries?.map((country: Ulke) => (
                    <Option key={country.kod} value={country.kod}>
                      {country.ad}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="aciklama" label="Açıklama">
                <TextArea rows={4} placeholder="Sipariş ile ilgili notlar (opsiyonel)" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={16}>
              <Row gutter={16}>
                <Col xs={24} sm={8}>
                  <Form.Item
                    name="siparis_mektubu"
                    label={isEdit ? "Sipariş Mektubu (Güncelle)" : "Sipariş Mektubu (Zorunlu)"}
                    rules={isEdit ? [] : [{ required: true, message: 'Sipariş mektubu yüklenmesi zorunludur' }]}
                  >
                    <Upload
                      name="siparis_mektubu"
                      multiple={false}
                      maxCount={1}
                      beforeUpload={() => false}
                      accept=".pdf,.doc,.docx"
                      fileList={siparisMetkubu}
                      onChange={({ fileList }) => setSiparisMetkubu(fileList)}
                      listType="text"
                    >
                      <Button icon={<UploadOutlined />} size="small">
                        {isEdit ? 'Yeni PDF/DOC Yükle' : 'PDF/DOC Yükle'}
                      </Button>
                    </Upload>
                  </Form.Item>
                </Col>
                
                <Col xs={24} sm={8}>
                  <Form.Item
                    name="maliyet_hesabi"
                    label={isEdit ? "Maliyet Hesabı (Güncelle)" : "Maliyet Hesabı (Zorunlu)"}
                    rules={isEdit ? [] : [{ required: true, message: 'Maliyet hesap tablosu yüklenmesi zorunludur' }]}
                  >
                    <Upload
                      name="maliyet_hesabi"
                      multiple={false}
                      maxCount={1}
                      beforeUpload={() => false}
                      accept=".xls,.xlsx,.pdf"
                      fileList={maliyetHesabi}
                      onChange={({ fileList }) => setMaliyetHesabi(fileList)}
                      listType="text"
                    >
                      <Button icon={<UploadOutlined />} size="small">
                        {isEdit ? 'Yeni Excel/PDF Yükle' : 'Excel/PDF Yükle'}
                      </Button>
                    </Upload>
                  </Form.Item>
                </Col>

                <Col xs={24} sm={8}>
                  <Form.Item name="ek_dosyalar" label="Ek Dosyalar (İsteğe Bağlı)">
                    <Upload
                      name="ek_dosyalar"
                      multiple={true}
                      maxCount={5}
                      beforeUpload={() => false}
                      accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                      fileList={ekDosyalar}
                      onChange={({ fileList }) => setEkDosyalar(fileList)}
                      listType="text"
                    >
                      <Button icon={<UploadOutlined />} size="small">
                        Ek Dosya Ekle (Max 5)
                      </Button>
                    </Upload>
                  </Form.Item>
                </Col>
              </Row>
            </Col>
          </Row>
        </StyledCard>

        <Card title="Sipariş Kalemleri" style={{ marginTop: 16 }}>
          <OrderItemsTable>
            <Table
              dataSource={orderItems}
              columns={orderItemColumns}
              rowKey={(record) => record.id || `temp-${Date.now()}-${Math.random()}`}
              pagination={false}
              size="small"
              locale={{ emptyText: 'Henüz kalem eklenmemiş' }}
              summary={() => (
                <Table.Summary fixed>
                  <Table.Summary.Row>
                    <Table.Summary.Cell index={0} colSpan={6}>
                      <strong>Genel Toplam (USD)</strong>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={1}>
                      <strong style={{ color: '#1890ff', fontSize: '16px' }}>
                        ${calculateTotal().toFixed(2)}
                      </strong>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={2} colSpan={2} />
                  </Table.Summary.Row>
                </Table.Summary>
              )}
            />
          </OrderItemsTable>
          
          <Button
            type="dashed"
            onClick={addOrderItem}
            icon={<PlusOutlined />}
            style={{ width: '100%', marginTop: 16 }}
          >
            Kalem Ekle
          </Button>
        </Card>

        {/* Ek Dosyalar (Edit Mode) */}
        {isEdit && orderData && (
          <Card title="Ek Dosyalar" style={{ marginTop: 16 }}>
            {orderData.dosyalar && Array.isArray(orderData.dosyalar) && orderData.dosyalar.length > 0 ? (
              <Table
                dataSource={orderData.dosyalar}
                rowKey="id"
                pagination={false}
                size="small"
                columns={[
                  {
                    title: 'Dosya Adı',
                    dataIndex: 'dosya',
                    key: 'dosya',
                    render: (dosya: string) => {
                      const fileName = dosya.split('/').pop();
                      return (
                        <Button type="link" href={dosya} target="_blank">
                          {fileName}
                        </Button>
                      );
                    },
                  },
                  {
                    title: 'Açıklama',
                    dataIndex: 'aciklama',
                    key: 'aciklama',
                    render: (text: string) => text || '-',
                  },
                  {
                    title: 'Yüklenme Tarihi',
                    dataIndex: 'yuklenme_tarihi',
                    key: 'yuklenme_tarihi',
                    render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
                  },
                ]}
              />
            ) : (
              <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                Bu siparişe henüz dosya eklenmemiş.
              </p>
            )}
          </Card>
        )}

        <Card style={{ marginTop: 16, textAlign: 'right' }}>
          <Space>
            <Button onClick={() => navigate('/sales/orders')}>
              İptal
            </Button>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={createMutation.isPending || updateMutation.isPending}
              disabled={orderItems.length === 0}
            >
              {isEdit ? 'Güncelle' : 'Kaydet'}
            </Button>
          </Space>
        </Card>
      </Form>
    </div>
  );
};

export default OrderForm;