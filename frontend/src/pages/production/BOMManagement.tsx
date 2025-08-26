import React, { useState } from 'react';
import { Card, Table, Button, Space, Tag, Row, Col, Typography, Divider, Tree, Statistic, Modal, Form, Input, InputNumber, Select, App, AutoComplete, Tooltip, Alert } from 'antd';
import { 
  ApartmentOutlined, 
  PlusOutlined, 
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileTextOutlined,
  BuildOutlined,
  MinusCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import styled from 'styled-components';

const { Title } = Typography;

const PageHeader = styled.div`
  background: linear-gradient(135deg, #13c2c2 0%, #08979c 100%);
  color: white;
  padding: 24px;
  margin: -24px -24px 24px -24px;
  border-radius: 0 0 8px 8px;
`;

const BOMManagement: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const { modal, message: messageApi } = App.useApp();
  
  // Modal states
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingBOM, setEditingBOM] = useState<any>(null);
  const [modalType, setModalType] = useState<'create' | 'edit'>('create');
  
  // Hierarchical view modal states
  const [isHierarchyModalVisible, setIsHierarchyModalVisible] = useState(false);
  const [selectedBOMHierarchy, setSelectedBOMHierarchy] = useState<any>(null);

  // BOM listesini çek
  const { data: bomListData, isLoading: bomLoading } = useQuery({
    queryKey: ['bom-list'],
    queryFn: () => productionService.getBOMList()
  });

  // Ürün listesini çek (BOM eşleştirme için)
  const { data: productsData } = useQuery({
    queryKey: ['products-for-bom'],
    queryFn: () => productionService.getProducts()
  });

  // Ürün listesini çek (bitmiş ürünler için)
  const { data: allProductsData, isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => productionService.getProducts()
  });

  // BOM stats için
  const { data: bomStatsData, isLoading: statsLoading } = useQuery({
    queryKey: ['bom-stats'],
    queryFn: productionService.getBOMStats
  });

  // Sipariş kalemlerini çek
  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => productionService.getOrders()
  });

  // Eşleştirilmemiş sipariş kalemlerini filtrele
  const unmatchedOrderItems = React.useMemo(() => {
    const orders = ordersData?.results || ordersData || [];
    const bomTemplates = bomListData?.results || [];
    
    // Tüm sipariş kalemlerini düzleştir
    const allOrderItems = orders.flatMap((order: any) => 
      order.kalemler?.map((item: any) => ({
        ...item,
        siparis_no: order.siparis_no,
        musteri_adi: order.musteri_adi,
        display_name: `${order.siparis_no} - ${item.urun_adi} (${item.adet || item.miktar || item.quantity || 'N/A'} adet)`
      })) || []
    );
    
    // Zaten BOM'u olan ürün ID'lerini al (API response'dan direkt)
    const matchedProductIds = bomTemplates
      .filter((template: any) => template.eslestirilen_urun)
      .map((template: any) => parseInt(template.eslestirilen_urun)); // parseInt ekle
    
    // Eşleştirilmemiş sipariş kalemlerini döndür (type comparison da fix)
    return allOrderItems.filter((item: any) => 
      !matchedProductIds.includes(parseInt(item.urun))
    );
  }, [ordersData, bomListData]);

  // Malzeme listesini çek (hammadde ve ara ürünler için)
  const { data: materialsData, isLoading: materialsLoading } = useQuery({
    queryKey: ['materials'],
    queryFn: () => productionService.getProducts() // Tüm ürünleri çek
  });

  // CRUD Mutations
  const createMutation = useMutation({
    mutationFn: productionService.createBOM,
    onSuccess: (newBOM) => {
      // Optimistic update for the list
      queryClient.setQueryData(['bom-list'], (old: any) => {
        if (!old) return { results: [newBOM], count: 1 };
        return {
          ...old,
          results: [...old.results, newBOM],
          count: old.count + 1
        };
      });
      
      // Invalidate all BOM related queries to refresh dependency data
      queryClient.invalidateQueries({ queryKey: ['bom-list'] });
      queryClient.invalidateQueries({ queryKey: ['bom-stats'] });
      
      messageApi.success('BOM başarıyla oluşturuldu');
      setIsModalVisible(false);
      form.resetFields();
    },
    onError: () => {
      messageApi.error('BOM oluşturulurken hata oluştu');
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => productionService.updateBOM(id, data),
    onSuccess: (updatedBOM) => {
      // Optimistic update for the list
      queryClient.setQueryData(['bom-list'], (old: any) => {
        if (!old) return { results: [updatedBOM], count: 1 };
        return {
          ...old,
          results: old.results.map((bom: any) => 
            bom.id === updatedBOM.id ? updatedBOM : bom
          )
        };
      });
      
      // Invalidate all BOM related queries to refresh dependency data
      queryClient.invalidateQueries({ queryKey: ['bom-list'] });
      queryClient.invalidateQueries({ queryKey: ['bom-stats'] });
      
      messageApi.success('BOM başarıyla güncellendi');
      setIsModalVisible(false);
      form.resetFields();
      setEditingBOM(null);
    },
    onError: () => {
      messageApi.error('BOM güncellenirken hata oluştu');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: productionService.deleteBOM,
    onMutate: async (bomId: number) => {
      await queryClient.cancelQueries({ queryKey: ['bom-list'] });
      const previousBOMs = queryClient.getQueryData(['bom-list']);
      
      queryClient.setQueryData(['bom-list'], (old: any) => {
        if (!old) return { results: [], count: 0 };
        return {
          ...old,
          results: old.results.filter((bom: any) => bom.id !== bomId),
          count: old.count - 1
        };
      });
      
      return { previousBOMs };
    },
    onSuccess: () => {
      messageApi.success('BOM başarıyla silindi');
    },
    onError: (error: any, bomId: number, context: any) => {
      if (context?.previousBOMs) {
        queryClient.setQueryData(['bom-list'], context.previousBOMs);
      }
      messageApi.error('BOM silinirken hata oluştu');
    },
    onSettled: () => {
      // Invalidate all BOM related queries to refresh dependency data
      queryClient.invalidateQueries({ queryKey: ['bom-list'] });
      queryClient.invalidateQueries({ queryKey: ['bom-stats'] });
    }
  });

  // Handler functions
  const handleCreate = () => {
    setModalType('create');
    setEditingBOM(null);
    form.resetFields();
    // İlk malzeme satırını otomatik ekle
    form.setFieldsValue({
      malzemeler: [{}]
    });
    setIsModalVisible(true);
  };

  const handleEdit = (template: any) => {
    setModalType('edit');
    setEditingBOM(template);
    
    // Ürün ID'sini sipariş kalemi ID'sine çevir
    let eslestirilenSiparisKalemi = template.eslestirilen_urun;
    
    if (template.eslestirilen_urun) {
      // Bu ürün ID'sine sahip sipariş kalemini bul
      const orders = ordersData?.results || ordersData || [];
      const matchedOrderItem = orders.flatMap((order: any) => 
        order.kalemler?.map((item: any) => ({
          ...item,
          siparis_no: order.siparis_no,
          unique_id: `${order.siparis_no}-${item.id}`
        })) || []
      ).find((item: any) => parseInt(item.urun) === parseInt(template.eslestirilen_urun));

      if (matchedOrderItem) {
        eslestirilenSiparisKalemi = matchedOrderItem.unique_id;
        // Successfully found matching order item
      } else {
        // No matching order item found, keep as product ID
      }
    }
    
    form.setFieldsValue({
      bom_tanimi: template.bom_tanimi,
      aciklama: template.aciklama,
      eslestirilen_urun: eslestirilenSiparisKalemi,
      malzemeler: template.malzemeler || []
    });
    setIsModalVisible(true);
  };

  const handleDelete = (bomId: number) => {
    modal.confirm({
      title: 'BOM Kaydını Sil',
      content: 'Bu BOM kaydını silmek istediğinizden emin misiniz?',
      okText: 'Evet, Sil',
      okType: 'danger',
      cancelText: 'İptal',
      onOk: () => deleteMutation.mutate(bomId)
    });
  };

  const handleModalOk = () => {
    form.validateFields()
      .then((values) => {
        // Sipariş kalemi seçildiyse, ürün ID'sini çıkar
        if (values.eslestirilen_urun && values.eslestirilen_urun.includes('-')) {
          // Format: "siparis_no-kalem_id"
          // Edit modal için TÜM sipariş kalemlerini kullan (sadece eşleşmemiş olanları değil)
          const orders = ordersData?.results || ordersData || [];
          const allOrderItems = orders.flatMap((order: any) => 
            order.kalemler?.map((item: any) => ({
              ...item,
              siparis_no: order.siparis_no,
              display_name: `${order.siparis_no} - ${item.urun_adi} (${item.adet || item.miktar || item.quantity || 'N/A'} adet)`
            })) || []
          );
          
          const selectedOrderItem = allOrderItems.find(item => 
            `${item.siparis_no}-${item.id}` === values.eslestirilen_urun
          );
          
          if (selectedOrderItem) {
            // Convert order item selection to product ID
            values.eslestirilen_urun = selectedOrderItem.urun;
          } else {
            console.error('Selected order item not found!', values.eslestirilen_urun);
          }
        }
        
        if (modalType === 'create') {
          createMutation.mutate(values);
        } else if (modalType === 'edit' && editingBOM) {
          updateMutation.mutate({ id: editingBOM.id, data: values });
        }
      })
      .catch((errorInfo) => {
        console.log('Validation failed:', errorInfo);
      });
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    setEditingBOM(null);
    form.resetFields();
  };

  const handleShowHierarchy = (record: any) => {
    setSelectedBOMHierarchy(record.hierarchical_structure);
    setIsHierarchyModalVisible(true);
  };

  // Convert hierarchical structure to Tree data format
  const convertToTreeData = (structure: any): any[] => {
    if (!structure || !structure.materials) return [];
    
    return structure.materials.map((material: any) => ({
      title: (
        <span>
          {material.missing_bom ? (
            <span style={{ color: '#ff4d4f' }}>
              <WarningOutlined style={{ marginRight: '4px' }} />
              {material.name} ({material.quantity} {material.unit})
              <Tag color="red" size="small" style={{ marginLeft: '8px' }}>
                BOM Eksik
              </Tag>
            </span>
          ) : (
            <span>
              {material.name} ({material.quantity} {material.unit})
              <Tag 
                color={material.type === 'hammadde' ? 'blue' : 'green'} 
                size="small" 
                style={{ marginLeft: '8px' }}
              >
                {material.type === 'hammadde' ? 'Hammadde' : 'Ara Ürün'}
              </Tag>
            </span>
          )}
        </span>
      ),
      key: `${material.name}-${Math.random()}`,
      children: material.children && material.children.length > 0 
        ? convertToTreeData({ materials: material.children[0]?.materials || [] })
        : undefined
    }));
  };

  // Transform data for display
  const bomList = (bomListData?.results || []).map((template: any) => ({
    key: template.id,
    id: template.id,
    bom_tanimi: template.bom_tanimi,
    aciklama: template.aciklama,
    malzemeler: template.malzemeler || [],
    eslestirilen_urun_adi: template.eslestirilen_urun_adi,
    eslestirilen_urun: template.eslestirilen_urun, // Bu field eksikti!
    guncellenme_tarihi: template.guncellenme_tarihi,
    malzeme_sayisi: template.malzemeler ? template.malzemeler.length : 0,
    missing_dependencies: template.missing_dependencies || [],
    is_complete: template.is_complete || false,
    hierarchical_structure: template.hierarchical_structure || {}
  }));

  const columns = [
    {
      title: 'BOM Tanımı',
      dataIndex: 'bom_tanimi',
      key: 'bom_tanimi',
      width: 250,
      render: (text: string, record: any) => {
        const { is_complete, missing_dependencies } = record;
        
        if (!is_complete && missing_dependencies.length > 0) {
          return (
            <Tooltip 
              title={
                <div>
                  <div style={{ marginBottom: '8px' }}>
                    <strong>Eksik BOM'lar:</strong>
                  </div>
                  {missing_dependencies.map((dep: string, index: number) => (
                    <div key={index}>• {dep}</div>
                  ))}
                  <div style={{ marginTop: '8px', fontSize: '12px', opacity: 0.8 }}>
                    Bu BOM üretimde kullanılamaz
                  </div>
                </div>
              }
            >
              <span style={{ color: '#ff4d4f', cursor: 'help' }}>
                <WarningOutlined style={{ marginRight: '8px' }} />
                <strong>{text}</strong>
              </span>
            </Tooltip>
          );
        }
        
        return (
          <span style={{ color: '#52c41a' }}>
            <CheckCircleOutlined style={{ marginRight: '8px' }} />
            <strong>{text}</strong>
          </span>
        );
      }
    },
    {
      title: 'Malzeme Sayısı',
      dataIndex: 'malzeme_sayisi',
      key: 'malzeme_sayisi',
      width: 120,
      render: (count: number) => (
        <Tag color="blue" icon={<FileTextOutlined />}>
          {count} Malzeme
        </Tag>
      )
    },
    {
      title: 'Eşleştirilmiş Sipariş',
      dataIndex: 'eslestirilen_urun_adi',
      key: 'eslestirilen_urun',
      width: 400,
      render: (productName: string, record: any) => {
        // BOM'un eşleştirildiği ürün ID'sini al
        const matchedProductId = record.eslestirilen_urun;
        
        
        if (matchedProductId) {
          // Bu ürün ID'sine sahip sipariş kalemini TÜM order item'larda bul (sadece unmatched'larda değil)
          const orders = ordersData?.results || ordersData || [];
          const allOrderItems = orders.flatMap((order: any) => 
            order.kalemler?.map((item: any) => ({
              ...item,
              siparis_no: order.siparis_no,
              display_name: `${order.siparis_no} - ${item.urun_adi} (${item.adet || item.miktar || item.quantity || 'N/A'} adet)`
            })) || []
          );
          
          const matchedOrderItem = allOrderItems.find((item: any) => 
            parseInt(item.urun) === parseInt(matchedProductId)
          );



          if (matchedOrderItem) {
            return (
              <Tag color="green" icon={<CheckCircleOutlined />}>
                {matchedOrderItem.display_name}
              </Tag>
            );
          } else {
            // Sipariş kalemi bulunamadı, ürün adını göster
            return (
              <Tag color="blue" icon={<CheckCircleOutlined />}>
                {productName || `Ürün (ID: ${matchedProductId})`}
              </Tag>
            );
          }
        } else {
          // Bu bir ara ürün BOM'u mu? Ana BOM'larda kullanılıyor mu kontrol et
          const bomTemplates = bomListData?.results || [];
          const usedInMainBOMs = bomTemplates.filter((mainBOM: any) => {
            const malzemeler = mainBOM.malzemeler || [];
            return malzemeler.some((malzeme: any) => 
              malzeme.ara_urun_bom_id === record.id
            );
          });
          
          if (usedInMainBOMs.length > 0) {
            return (
              <Tag color="purple" icon={<CheckCircleOutlined />}>
                {usedInMainBOMs.length} Ana BOM'da Kullanılıyor
              </Tag>
            );
          } else {
            return (
              <Tag color="orange" icon={<WarningOutlined />}>
                Eşleştirilmemiş
              </Tag>
            );
          }
        }
      }
    },
    {
      title: 'Açıklama',
      dataIndex: 'aciklama',
      key: 'aciklama',
      width: 250,
      ellipsis: true,
      render: (text: string) => text || '-'
    },
    {
      title: 'Güncelleme Tarihi',
      dataIndex: 'guncellenme_tarihi',
      key: 'guncellenme_tarihi',
      width: 160,
      render: (date: string) => new Date(date).toLocaleDateString('tr-TR')
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 280,
      render: (record: any) => (
        <Space>
          <Button 
            size="small" 
            icon={<ApartmentOutlined />}
            onClick={() => handleShowHierarchy(record)}
          >
            BOM Ağacı
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
            onClick={() => handleDelete(record.id)}
          >
            Sil
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <PageHeader>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          <ApartmentOutlined style={{ marginRight: '12px' }} />
          BOM (Ürün Reçetesi) Yönetimi
        </Title>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
          Ürün reçetelerini oluşturun ve yönetin
        </p>
      </PageHeader>

      {/* BOM İstatistikleri */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={12} sm={6}>
          <Card loading={bomLoading}>
            <Statistic
              title="Toplam BOM"
              value={bomListData?.count || 0}
              prefix={<ApartmentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card loading={statsLoading}>
            <Statistic
              title="Toplam Ürün"
              value={bomStatsData?.totalBOM || 0}
              prefix={<BuildOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card loading={productsLoading}>
            <Statistic
              title="Toplam Malzeme"
              value={allProductsData?.count || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card loading={bomLoading}>
            <Statistic
              title="Ortalama Malzeme/Ürün"
              value={bomListData?.count && bomStatsData?.totalBOM ? 
                Math.round((bomListData.count / bomStatsData.totalBOM) * 10) / 10 : 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {/* BOM Listesi */}
        <Col xs={24} lg={16}>
          <Card 
            title="BOM Listesi"
            extra={
              <Button 
                icon={<PlusOutlined />}
                onClick={handleCreate}
              >
                Yeni BOM
              </Button>
            }
          >
            <Table
              columns={columns}
              dataSource={bomList}
              rowKey="id"
              loading={bomLoading}
              pagination={{
                pageSize: 10,
                showSizeChanger: false,
                showTotal: (total, range) => `${range[0]}-${range[1]} / ${total} BOM`
              }}
              size="small"
            />
          </Card>
        </Col>

      </Row>

      {/* Son Güncellenen BOM'lar */}
      {!bomLoading && bomStatsData && bomStatsData.recentBOM && (
        <Card title="Son Güncellenen BOM'lar">
          <Row gutter={[16, 16]}>
            {bomStatsData.recentBOM.map((bom: any) => (
              <Col xs={24} sm={12} lg={8} key={bom.id}>
                <Card size="small" hoverable>
                  <div style={{ marginBottom: '8px' }}>
                    <strong>{bom.name}</strong>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    <div>Bileşen: {bom.components} adet</div>
                    <div>Tip: {bom.type}</div>
                    <div>Güncelleme: {new Date(bom.updated).toLocaleDateString('tr-TR')}</div>
                  </div>
                  <div style={{ marginTop: '8px' }}>
                    <Button 
                      size="small" 
                      type="link" 
                      icon={<EyeOutlined />}
                      onClick={() => {
                        // Recent BOM'lar için full veriyi bomList'den bul
                        const fullBOMData = bomList.find((fullBom: any) => fullBom.id === bom.id);
                        if (fullBOMData) {
                          handleShowHierarchy(fullBOMData);
                        }
                      }}
                    >
                      İncele
                    </Button>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* Geri Dön Butonu */}
      <Divider />
      <Space>
        <Button onClick={() => navigate('/production')}>
          ← Üretim Dashboard'a Dön
        </Button>
      </Space>

      {/* BOM Create/Edit Modal */}
      <Modal
        title={modalType === 'create' ? 'Yeni BOM Oluştur' : 'BOM Düzenle'}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        okText={modalType === 'create' ? 'Oluştur' : 'Güncelle'}
        cancelText="İptal"
        confirmLoading={createMutation.isLoading || updateMutation.isLoading}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          name="bomForm"
        >
          <Form.Item
            name="bom_tanimi"
            label="BOM Tanımı"
            rules={[{ required: true, message: 'Lütfen BOM tanımı giriniz!' }]}
          >
            <Input
              placeholder="Örn: 630kVA Trafo Reçetesi, Motor Sargı Reçetesi..."
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="eslestirilen_urun"
            label="Sipariş Kalemi Eşleştirme (Opsiyonel)"
            help="Bu BOM hangi sipariş kalemi için kullanılacak? Eşleştirme yaparsanız iş akışı tasarımında otomatik yüklenir."
          >
            <Select
              placeholder="BOM'u bir sipariş kalemi ile eşleştirin..."
              allowClear
              showSearch
              loading={ordersLoading}
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={(() => {
                // Edit modal için TÜM sipariş kalemlerini göster
                // Create modal için sadece eşleşmemiş olanları göster
                const itemsToShow = modalType === 'edit' 
                  ? ordersData?.results?.flatMap((order: any) => 
                      order.kalemler?.map((item: any) => ({
                        ...item,
                        siparis_no: order.siparis_no,
                        display_name: `${order.siparis_no} - ${item.urun_adi} (${item.adet || item.miktar || item.quantity || 'N/A'} adet)`
                      })) || []
                    ) || []
                  : unmatchedOrderItems;
                
                return itemsToShow.map((item: any) => ({
                  value: `${item.siparis_no}-${item.id}`,
                  label: item.display_name,
                  key: `${item.siparis_no}-${item.id}`,
                  urun_id: item.urun
                }));
              })()}
            />
          </Form.Item>

          <Form.Item
            name="aciklama"
            label="Açıklama (İsteğe Bağlı)"
          >
            <Input.TextArea
              placeholder="Bu BOM hakkında ek bilgiler..."
              rows={2}
            />
          </Form.Item>

          <Divider orientation="left">Malzeme Listesi</Divider>

          <Form.List name="malzemeler">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Row key={key} gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={6}>
                      <Form.Item
                        {...restField}
                        name={[name, 'malzeme_adi']}
                        label={key === 0 ? 'Malzeme Adı' : ''}
                        rules={[{ required: true, message: 'Malzeme adı gerekli!' }]}
                      >
                        <AutoComplete
                          placeholder="Malzeme adı yazın veya listeden seçin..."
                          options={(materialsData?.results || [])
                            .map((product: any) => ({
                              value: product.ad,
                              label: `${product.ad} (${product.kod})`
                            }))}
                          filterOption={(inputValue, option) =>
                            option?.label?.toLowerCase().includes(inputValue.toLowerCase()) || false
                          }
                        />
                      </Form.Item>
                    </Col>
                    <Col span={3}>
                      <Form.Item
                        {...restField}
                        name={[name, 'tur']}
                        label={key === 0 ? 'Tür' : ''}
                        rules={[{ required: true, message: 'Tür seçin!' }]}
                      >
                        <Select placeholder="Tür">
                          <Select.Option value="hammadde">Hammadde</Select.Option>
                          <Select.Option value="ara_urun">Ara Ürün</Select.Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col span={3}>
                      <Form.Item
                        {...restField}
                        name={[name, 'birim']}
                        label={key === 0 ? 'Birim' : ''}
                        rules={[{ required: true, message: 'Birim gerekli!' }]}
                      >
                        <Select placeholder="Birim">
                          <Select.Option value="adet">Adet</Select.Option>
                          <Select.Option value="kg">Kilogram</Select.Option>
                          <Select.Option value="m">Metre</Select.Option>
                          <Select.Option value="m2">Metrekare</Select.Option>
                          <Select.Option value="lt">Litre</Select.Option>
                          <Select.Option value="gr">Gram</Select.Option>
                          <Select.Option value="ton">Ton</Select.Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...restField}
                        name={[name, 'miktar']}
                        label={key === 0 ? 'Miktar' : ''}
                        rules={[{ required: true, message: 'Miktar gerekli!' }]}
                      >
                        <InputNumber
                          placeholder="0"
                          min={0}
                          step={0.01}
                          style={{ width: '100%' }}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item shouldUpdate noStyle>
                        {() => {
                          const currentType = form.getFieldValue(['malzemeler', name, 'tur']);
                          const isSubProduct = currentType === 'ara_urun';
                          
                          return (
                            <Form.Item
                              {...restField}
                              name={[name, 'ara_urun_bom_id']}
                              label={key === 0 ? 'Ara Ürün BOM\'u' : ''}
                              help={key === 0 ? 'Ara ürün seçilmişse BOM\'unu seçin' : ''}
                            >
                              <Select
                                placeholder={isSubProduct ? 'BOM seçin...' : 'Önce ara ürün seçin'}
                                disabled={!isSubProduct}
                                allowClear
                                showSearch
                                filterOption={(input, option) =>
                                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                                }
                                options={bomListData?.results?.map((bom: any) => ({
                                  value: bom.id,
                                  label: bom.bom_tanimi,
                                  key: bom.id
                                })) || []}
                              />
                            </Form.Item>
                          );
                        }}
                      </Form.Item>
                    </Col>
                    <Col span={2}>
                      {key === 0 ? <div style={{ height: '32px' }}></div> : null}
                      <Button
                        type="text"
                        icon={<MinusCircleOutlined />}
                        onClick={() => remove(name)}
                        danger
                        style={{ marginTop: key === 0 ? '32px' : '0' }}
                      />
                    </Col>
                  </Row>
                ))}
                <Form.Item>
                  <Button
                    type="dashed"
                    onClick={() => add()}
                    block
                    icon={<PlusOutlined />}
                  >
                    Malzeme Satırı Ekle
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>

      {/* Hierarchical BOM Structure Modal */}
      <Modal
        title="BOM Ağaç Yapısı - Hammaddeye Kadar Görüntüleme"
        open={isHierarchyModalVisible}
        onCancel={() => setIsHierarchyModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsHierarchyModalVisible(false)}>
            Kapat
          </Button>
        ]}
        width={800}
      >
        {selectedBOMHierarchy && (
          <div>
            <Alert
              message="BOM Ağaç Yapısı"
              description={
                <div>
                  <div><strong>Ürün:</strong> {selectedBOMHierarchy.name}</div>
                  <div style={{ marginTop: '8px' }}>
                    • <span style={{ color: '#1890ff' }}>Mavi etiketler</span>: Hammadde
                  </div>
                  <div>
                    • <span style={{ color: '#52c41a' }}>Yeşil etiketler</span>: Ara ürün
                  </div>
                  <div>
                    • <span style={{ color: '#ff4d4f' }}>Kırmızı etiketler</span>: BOM'u eksik olan ara ürün
                  </div>
                </div>
              }
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />
            
            <Tree
              treeData={convertToTreeData(selectedBOMHierarchy)}
              defaultExpandAll
              showLine={{ showLeafIcon: false }}
              style={{ marginTop: '16px' }}
            />
            
            {selectedBOMHierarchy.materials?.some((m: any) => m.missing_bom) && (
              <Alert
                message="Dikkat: Eksik BOM'lar Tespit Edildi"
                description="Bu ürün için eksik ara ürün BOM'ları var. Üretim öncesi bu BOM'ları tanımlamanız gerekiyor."
                type="warning"
                showIcon
                style={{ marginTop: '16px' }}
              />
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BOMManagement;