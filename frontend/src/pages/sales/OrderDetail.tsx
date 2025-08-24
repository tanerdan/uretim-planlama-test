import React from 'react';
import { 
  Card, 
  Descriptions, 
  Table, 
  Tag, 
  Button, 
  Space, 
  Typography, 
  Row, 
  Col,
  Divider,
  Spin,
  Alert
} from 'antd';
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { salesService } from '../../services/salesService';
import { SiparisKalem } from '../../types';
import dayjs from 'dayjs';

const { Title } = Typography;

const OrderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const orderId = parseInt(id || '0');

  const { data: order, isLoading, error } = useQuery({
    queryKey: ['order', orderId],
    queryFn: () => salesService.getOrderById(orderId),
    enabled: !!orderId,
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

  const dovizLabels = {
    'USD': 'USD',
    'EUR': 'EUR',
    'TRY': 'TRY',
    'GBP': 'GBP'
  };

  const ulkeLabels = {
    'TR': 'Türkiye',
    'US': 'ABD',
    'DE': 'Almanya',
    'FR': 'Fransa',
    'IT': 'İtalya',
    'ES': 'İspanya',
    'NL': 'Hollanda',
    'BE': 'Belçika',
    'CH': 'İsviçre',
    'AT': 'Avusturya',
    'UK': 'İngiltere'
  };

  const itemColumns = [
    {
      title: 'Ürün',
      dataIndex: 'urun_adi',
      key: 'urun_adi',
      width: 200,
    },
    {
      title: 'Miktar',
      dataIndex: 'miktar',
      key: 'miktar',
      width: 80,
      align: 'right' as const,
    },
    {
      title: 'Birim Fiyat',
      dataIndex: 'birim_fiyat',
      key: 'birim_fiyat',
      width: 100,
      align: 'right' as const,
      render: (price: any, record: SiparisKalem) => {
        const amount = parseFloat(price) || 0;
        return `${record.doviz} ${amount.toFixed(2)}`;
      },
    },
    {
      title: 'Para Birimi',
      dataIndex: 'doviz',
      key: 'doviz',
      width: 80,
      render: (doviz: string) => dovizLabels[doviz as keyof typeof dovizLabels] || doviz,
    },
    {
      title: 'Kur',
      dataIndex: 'kur',
      key: 'kur',
      width: 80,
      align: 'right' as const,
      render: (kur: any) => {
        const rate = parseFloat(kur) || 1;
        return rate.toFixed(4);
      },
    },
    {
      title: 'USD Fiyat',
      dataIndex: 'birim_fiyat_usd',
      key: 'birim_fiyat_usd',
      width: 100,
      align: 'right' as const,
      render: (price: any) => {
        const amount = parseFloat(price) || 0;
        return `$${amount.toFixed(2)}`;
      },
    },
    {
      title: 'Toplam (USD)',
      key: 'toplam_usd',
      width: 100,
      align: 'right' as const,
      render: (_, record: SiparisKalem) => {
        const miktar = parseFloat(record.miktar as any) || 0;
        const fiyat = parseFloat(record.birim_fiyat_usd as any) || 0;
        const total = miktar * fiyat;
        return `$${total.toFixed(2)}`;
      },
    },
    {
      title: 'Teslim Tarihi',
      dataIndex: 'teslim_tarihi',
      key: 'teslim_tarihi',
      width: 120,
      render: (date: string) => date ? dayjs(date).format('DD.MM.YYYY') : '-',
    },
    {
      title: 'Son Kullanıcı Ülke',
      dataIndex: 'son_kullanici_ulke',
      key: 'son_kullanici_ulke',
      width: 120,
      render: (ulke: string) => ulkeLabels[ulke as keyof typeof ulkeLabels] || ulke,
    },
    {
      title: 'Açıklama',
      dataIndex: 'notlar',
      key: 'notlar',
      width: 150,
      render: (notlar: string) => notlar || '-',
    },
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !order) {
    return (
      <Alert
        message="Hata"
        description="Sipariş detayları yüklenirken hata oluştu."
        type="error"
        showIcon
        action={
          <Button onClick={() => navigate('/sales/orders')}>
            Geri Dön
          </Button>
        }
      />
    );
  }

  const totalAmount = order.kalemler?.reduce((sum, item) => {
    const miktar = parseFloat(item.miktar as any) || 0;
    const fiyat = parseFloat(item.birim_fiyat_usd as any) || 0;
    return sum + (miktar * fiyat);
  }, 0) || 0;

  return (
    <div>
      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Button 
                icon={<ArrowLeftOutlined />} 
                onClick={() => navigate('/sales/orders')}
              >
                Geri
              </Button>
              <Title level={3} style={{ margin: 0 }}>
                Sipariş Detayı - {order.siparis_no}
              </Title>
            </Space>
          </Col>
          <Col>
            <Button 
              type="primary" 
              icon={<EditOutlined />}
              onClick={() => navigate(`/sales/orders/${order.id}/edit`)}
            >
              Düzenle
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Sipariş Bilgileri */}
      <Card title="Sipariş Bilgileri" style={{ marginBottom: 16 }}>
        <Descriptions bordered size="small" column={2}>
          <Descriptions.Item label="Sipariş No">{order.siparis_no}</Descriptions.Item>
          <Descriptions.Item label="Durum">
            <Tag color={statusColors[order.durum as keyof typeof statusColors]}>
              {statusLabels[order.durum as keyof typeof statusLabels] || order.durum}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Müşteri">{order.musteri_adi}</Descriptions.Item>
          <Descriptions.Item label="Müşteri Ülke">
            {ulkeLabels[order.musteri_ulke as keyof typeof ulkeLabels] || order.musteri_ulke}
          </Descriptions.Item>
          <Descriptions.Item label="Sipariş Tarihi">
            {dayjs(order.tarih).format('DD.MM.YYYY')}
          </Descriptions.Item>
          <Descriptions.Item label="Toplam Tutar">
            <strong>${totalAmount.toFixed(2)}</strong>
          </Descriptions.Item>
          <Descriptions.Item label="Oluşturulma" span={2}>
            {dayjs(order.olusturulma_tarihi).format('DD.MM.YYYY HH:mm')}
          </Descriptions.Item>
          {order.notlar && (
            <Descriptions.Item label="Notlar" span={2}>
              {order.notlar}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      {/* Sipariş Kalemleri */}
      <Card title={`Sipariş Kalemleri (${order.kalemler?.length || 0} kalem)`}>
        <Table
          columns={itemColumns}
          dataSource={order.kalemler || []}
          rowKey="id"
          pagination={false}
          scroll={{ x: 1200 }}
          size="small"
          summary={(pageData) => {
            const total = pageData.reduce((sum, record) => {
              const miktar = parseFloat(record.miktar as any) || 0;
              const fiyat = parseFloat(record.birim_fiyat_usd as any) || 0;
              return sum + (miktar * fiyat);
            }, 0);
            return (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0} colSpan={6}>
                  <strong>Toplam</strong>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={6}>
                  <strong>${total.toFixed(2)}</strong>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={7} colSpan={3} />
              </Table.Summary.Row>
            );
          }}
        />
      </Card>

      {/* Dosyalar */}
      {order.dosyalar && Array.isArray(order.dosyalar) && order.dosyalar.length > 0 ? (
        <Card title="Ek Dosyalar" style={{ marginTop: 16 }}>
          <Table
            dataSource={order.dosyalar}
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
        </Card>
      ) : (
        <Card title="Ek Dosyalar" style={{ marginTop: 16 }}>
          <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
            Bu siparişe henüz dosya eklenmemiş.
          </p>
        </Card>
      )}
    </div>
  );
};

export default OrderDetail;