import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  Button, 
  Space, 
  Typography, 
  Row, 
  Col, 
  Input, 
  Select, 
  Form,
  message,
  Drawer,
  List,
  Tag,
  Divider,
  Modal,
  InputNumber,
  Switch
} from 'antd';
import { 
  SaveOutlined, 
  UndoOutlined, 
  RedoOutlined,
  DeleteOutlined,
  PlusOutlined,
  SettingOutlined,
  ArrowRightOutlined,
  NodeIndexOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productionService } from '../../services/productionService';
import styled from 'styled-components';

const { Title, Text } = Typography;
const { Option } = Select;

// Styled Components
const DesignerContainer = styled.div`
  display: flex;
  height: calc(100vh - 200px);
  gap: 16px;
`;

const LeftPanel = styled.div`
  width: 300px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
`;

const Canvas = styled.div`
  flex: 1;
  background: white;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
`;

const CanvasContent = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
`;

const OperationNode = styled.div<{ selected?: boolean; x: number; y: number }>`
  position: absolute;
  left: ${props => props.x}px;
  top: ${props => props.y}px;
  width: 200px;
  min-height: 80px;
  background: ${props => props.selected ? '#e6f7ff' : 'white'};
  border: 2px solid ${props => props.selected ? '#1890ff' : '#d9d9d9'};
  border-radius: 8px;
  padding: 12px;
  cursor: move;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 10;
  
  &:hover {
    border-color: #1890ff;
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
  }
`;

const DraggableOperation = styled.div`
  padding: 8px 12px;
  margin: 4px 0;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;
  
  &:hover {
    border-color: #1890ff;
    box-shadow: 0 2px 4px rgba(24, 144, 255, 0.2);
  }
  
  &:active {
    cursor: grabbing;
    transform: scale(0.95);
  }
`;

const Connection = styled.svg`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 5;
`;

interface OperationNodeType {
  id: string;
  x: number;
  y: number;
  title: string;
  description: string;
  duration: number;
  setupTime: number;
  stationId: number;
  stationName: string;
  materials: string[];
}

interface ConnectionType {
  from: string;
  to: string;
}

const WorkflowDesigner: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [form] = Form.useForm();
  
  // States
  const [workflowData, setWorkflowData] = useState({
    kod: '',
    ad: '',
    urun: null,
    tip: 'seri',
    aciklama: ''
  });
  const [nodes, setNodes] = useState<OperationNodeType[]>([]);
  const [connections, setConnections] = useState<ConnectionType[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState<string | null>(null);
  const [operationDrawerOpen, setOperationDrawerOpen] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [editNodeDrawerOpen, setEditNodeDrawerOpen] = useState(false);
  const [editingNode, setEditingNode] = useState<OperationNodeType | null>(null);
  const [selectedOrderItem, setSelectedOrderItem] = useState<any>(null);
  const [bomMaterials, setBomMaterials] = useState<any[]>([]);
  
  // API Queries
  const { data: stationsData, error: stationsError, isLoading: stationsLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: productionService.getStations
  });

  const { data: operationsData, error: operationsError, isLoading: operationsLoading } = useQuery({
    queryKey: ['standard-operations'],
    queryFn: productionService.getStandardOperations
  });

  // Safely extract arrays
  const stations = stationsData?.results || stationsData || [];
  const standardOperations = operationsData?.results || operationsData || [];

  const { data: productsData, error: productsError } = useQuery({
    queryKey: ['products'],
    queryFn: productionService.getProducts
  });

  // Safely extract products array
  const products = productsData?.results || productsData || [];

  // Pending orders query
  const { data: ordersData } = useQuery({
    queryKey: ['pending-orders'],
    queryFn: () => productionService.getOrders({ durum: 'beklemede' })
  });

  // Extract pending order items
  const pendingOrderItems = React.useMemo(() => {
    const orders = ordersData?.results || ordersData || [];
    const items: any[] = [];
    
    orders.forEach((order: any) => {
      order.kalemler?.forEach((item: any) => {
        items.push({
          ...item,
          siparis_no: order.siparis_no,
          siparis_id: order.id,
          musteri_adi: order.musteri_adi
        });
      });
    });
    
    return items;
  }, [ordersData]);

  // Debug log errors and data
  React.useEffect(() => {
    if (stationsError) console.error('Stations error:', stationsError);
    if (operationsError) console.error('Operations error:', operationsError);  
    if (productsError) console.error('Products error:', productsError);
    
    console.log('API Data:', {
      stationsData,
      operationsData, 
      productsData,
      stations: stations.length,
      standardOperations: standardOperations.length,
      products: products.length
    });
  }, [stationsData, operationsData, productsData, stationsError, operationsError, productsError]);

  const { data: workflow } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => productionService.getWorkflow(id!),
    enabled: !!id
  });

  // Load workflow data if editing
  useEffect(() => {
    if (workflow) {
      setWorkflowData({
        kod: workflow.kod,
        ad: workflow.ad,
        urun: workflow.urun,
        tip: workflow.tip,
        aciklama: workflow.aciklama || ''
      });
      form.setFieldsValue(workflow);
      
      // Convert operations to nodes
      if (workflow.operasyonlar) {
        const loadedNodes = workflow.operasyonlar.map((op: any, index: number) => ({
          id: op.id.toString(),
          x: 100 + (index * 250),
          y: 100,
          title: op.operasyon_adi,
          description: op.aciklama || '',
          duration: parseFloat(op.standart_sure),
          setupTime: parseFloat(op.hazirlik_suresi),
          stationId: op.istasyon,
          stationName: op.istasyon_adi,
          materials: op.operasyon_malzemeleri || []
        }));
        setNodes(loadedNodes);
      }
    }
  }, [workflow, form]);

  // Drag & Drop Handlers
  const handleDragStart = (e: React.DragEvent, operationType: 'standard' | 'custom' | 'material', data: any) => {
    e.dataTransfer.setData('operationType', operationType);
    e.dataTransfer.setData('operationData', JSON.stringify(data));
  };

  const handleCanvasDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleCanvasDrop = (e: React.DragEvent) => {
    e.preventDefault();
    
    if (!canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const operationType = e.dataTransfer.getData('operationType');
    const operationData = JSON.parse(e.dataTransfer.getData('operationData'));
    
    if (operationType === 'standard') {
      const newNode: OperationNodeType = {
        id: Date.now().toString(),
        x: Math.max(0, x - 100),
        y: Math.max(0, y - 40),
        title: operationData.ad,
        description: operationData.aciklama || '',
        duration: parseFloat(operationData.tahmini_sure_birim || 0),
        setupTime: 0,
        stationId: 0, // Will be set later
        stationName: 'İstasyon Seçiniz',
        materials: []
      };
      
      setNodes(prev => [...prev, newNode]);
      setSelectedNode(newNode.id);
    } else if (operationType === 'material') {
      // Material dropped on canvas - find closest node
      const closestNode = findClosestNode(x, y);
      if (closestNode) {
        attachMaterialToNode(closestNode.id, operationData);
      }
    }
  };

  // Helper functions for material attachment
  const findClosestNode = (x: number, y: number) => {
    let closest = null;
    let minDistance = Infinity;
    
    nodes.forEach(node => {
      const distance = Math.sqrt(
        Math.pow(node.x + 100 - x, 2) + Math.pow(node.y + 40 - y, 2)
      );
      if (distance < minDistance && distance < 150) { // Within 150px
        minDistance = distance;
        closest = node;
      }
    });
    
    return closest;
  };

  const attachMaterialToNode = (nodeId: string, material: any) => {
    setNodes(prev => prev.map(node => {
      if (node.id === nodeId) {
        const newMaterials = [...(node.materials || []), material.malzeme_adi];
        return { ...node, materials: newMaterials };
      }
      return node;
    }));
    
    message.success(`${material.malzeme_adi} operasyona eklendi!`);
  };

  // Node Interaction Handlers
  const handleNodeMouseDown = (e: React.MouseEvent, nodeId: string) => {
    if (isConnecting) {
      if (connectionStart) {
        // Complete connection
        if (connectionStart !== nodeId) {
          setConnections(prev => [...prev, { from: connectionStart, to: nodeId }]);
        }
        setIsConnecting(false);
        setConnectionStart(null);
      } else {
        // Start connection
        setConnectionStart(nodeId);
      }
      return;
    }
    
    e.preventDefault();
    setIsDragging(true);
    setSelectedNode(nodeId);
    
    const rect = (e.target as HTMLElement).getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  const handleNodeDoubleClick = (nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (node) {
      setEditingNode(node);
      setEditNodeDrawerOpen(true);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !selectedNode || !canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - dragOffset.x;
    const y = e.clientY - rect.top - dragOffset.y;
    
    setNodes(prev => prev.map(node => 
      node.id === selectedNode 
        ? { ...node, x: Math.max(0, x), y: Math.max(0, y) }
        : node
    ));
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Utility Functions
  const deleteNode = (nodeId: string) => {
    // For now, just remove from local state (no API call needed for nodes)
    // Individual nodes are part of the workflow, not separate API entities
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    setConnections(prev => prev.filter(conn => conn.from !== nodeId && conn.to !== nodeId));
    if (selectedNode === nodeId) {
      setSelectedNode(null);
    }
    message.success('Operasyon silindi!');
  };

  const updateNode = (nodeId: string, updates: Partial<OperationNodeType>) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId 
        ? { ...node, ...updates }
        : node
    ));
  };

  // Handle order item selection
  const handleOrderItemSelect = async (orderItem: any) => {
    setSelectedOrderItem(orderItem);
    
    try {
      // Fetch BOM materials for the selected product
      console.log('Selected order item:', orderItem);
      const bomData = await productionService.getBOMByProduct(orderItem.urun);
      console.log('BOM Data:', bomData);
      
      if (bomData && bomData.malzemeler) {
        setBomMaterials(bomData.malzemeler);
        message.success(`${orderItem.urun_adi} için BOM yüklendi! (${bomData.malzemeler.length} malzeme)`);
      } else {
        setBomMaterials([]);
        message.warning(`${orderItem.urun_adi} için BOM tanımlanmamış!`);
      }
      
      // Auto-fill workflow settings with order info
      setWorkflowData(prev => ({
        ...prev,
        urun: orderItem.urun,
        ad: `${orderItem.urun_adi} - İş Akışı`,
        kod: `WF-${orderItem.siparis_no}-${Date.now()}`
      }));
      
      form.setFieldsValue({
        urun: orderItem.urun,
        ad: `${orderItem.urun_adi} - İş Akışı`,
        kod: `WF-${orderItem.siparis_no}-${Date.now()}`
      });
      
    } catch (error) {
      console.error('BOM fetch error:', error);
      setBomMaterials([]);
      message.error('BOM verileri yüklenemedi!');
    }
  };

  const getConnectionPath = (from: OperationNodeType, to: OperationNodeType) => {
    const startX = from.x + 200;
    const startY = from.y + 40;
    const endX = to.x;
    const endY = to.y + 40;
    
    const midX = (startX + endX) / 2;
    
    return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`;
  };

  // Mutations
  const queryClient = useQueryClient();
  
  const createWorkflowMutation = useMutation({
    mutationFn: productionService.createWorkflow,
    onSuccess: () => {
      message.success('İş akışı başarıyla oluşturuldu!');
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      navigate('/production/workflows');
    },
    onError: (error) => {
      console.error('Create workflow error:', error);
      message.error('İş akışı oluşturulurken hata oluştu!');
    }
  });

  const updateWorkflowMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => 
      productionService.updateWorkflow(id, data),
    onSuccess: () => {
      message.success('İş akışı başarıyla güncellendi!');
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', id] });
      navigate('/production/workflows');
    },
    onError: (error) => {
      console.error('Update workflow error:', error);
      message.error('İş akışı güncellenirken hata oluştu!');
    }
  });

  // Save Workflow
  const saveWorkflow = async () => {
    try {
      // Validate form
      const formValues = await form.validateFields();
      
      const workflowPayload = {
        ...workflowData,
        ...formValues,
        operasyonlar: nodes.map((node, index) => ({
          sira_no: index + 1,
          operasyon_adi: node.title,
          aciklama: node.description,
          standart_sure: node.duration.toString(),
          hazirlik_suresi: node.setupTime.toString(),
          istasyon: node.stationId,
          operasyon_malzemeleri: node.materials
        })),
        // Save connections for future use
        workflow_connections: connections
      };
      
      if (id) {
        updateWorkflowMutation.mutate({ id, data: workflowPayload });
      } else {
        createWorkflowMutation.mutate(workflowPayload);
      }
    } catch (error) {
      message.error('Lütfen tüm zorunlu alanları doldurun!');
    }
  };

  // Loading state
  if (stationsLoading || operationsLoading) {
    return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <Title level={3}>İş Akışı Editörü Yükleniyor...</Title>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={3} style={{ margin: 0 }}>
              <NodeIndexOutlined style={{ marginRight: 8 }} />
              {id ? 'İş Akışı Düzenle' : 'Yeni İş Akışı Tasarla'}
            </Title>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<SettingOutlined />} 
                onClick={() => setSettingsModalOpen(true)}
              >
                Ayarlar
              </Button>
              <Button 
                type="primary" 
                icon={<SaveOutlined />}
                onClick={saveWorkflow}
              >
                Kaydet
              </Button>
              <Button onClick={() => navigate('/production/workflows')}>
                İptal
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Designer */}
      <DesignerContainer>
        {/* Left Panel - Orders & Operations Palette */}
        <LeftPanel>
          <Title level={4}>Bekleyen Siparişler</Title>
          
          <div style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: 16 }}>
            {pendingOrderItems.map((orderItem, index) => (
              <div
                key={`${orderItem.siparis_id}-${index}`}
                style={{
                  margin: '4px 0',
                  padding: '8px',
                  border: selectedOrderItem?.id === orderItem.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  backgroundColor: selectedOrderItem?.id === orderItem.id ? '#e6f7ff' : 'white'
                }}
                onClick={() => handleOrderItemSelect(orderItem)}
              >
                <div style={{ fontSize: '12px', fontWeight: 'bold' }}>
                  {orderItem.siparis_no}
                </div>
                <div style={{ fontSize: '11px', color: '#666' }}>
                  {orderItem.urun_adi}
                </div>
                <div style={{ fontSize: '10px', color: '#999' }}>
                  {orderItem.miktar} {orderItem.birim}
                </div>
              </div>
            ))}
            
            {pendingOrderItems.length === 0 && (
              <div style={{ textAlign: 'center', color: '#999', padding: 16 }}>
                Bekleyen sipariş yok
              </div>
            )}
          </div>

          {selectedOrderItem && (
            <>
              <Divider>BOM Malzemeleri</Divider>
              
              {bomMaterials.length > 0 ? (
                <div style={{ maxHeight: '150px', overflowY: 'auto', marginBottom: 16 }}>
                  {bomMaterials.map((material, index) => (
                    <div
                      key={index}
                      style={{
                        margin: '4px 0',
                        padding: '6px 8px',
                        backgroundColor: '#f0f8ff',
                        border: '1px dashed #1890ff',
                        borderRadius: '4px',
                        cursor: 'grab',
                        fontSize: '11px'
                      }}
                      draggable
                      onDragStart={(e) => handleDragStart(e, 'material', material)}
                    >
                      <strong>{material.malzeme_adi}</strong>
                      <br />
                      <span style={{ color: '#666' }}>
                        {material.miktar} {material.birim}
                      </span>
                      <Tag size="small" color={material.tur === 'hammadde' ? 'blue' : 'orange'}>
                        {material.tur === 'hammadde' ? 'Hammadde' : 'Ara Ürün'}
                      </Tag>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '16px', 
                  background: '#fff7e6', 
                  border: '1px solid #ffd591', 
                  borderRadius: '4px',
                  marginBottom: 16
                }}>
                  <div style={{ marginBottom: 8, fontSize: '12px', color: '#fa8c16' }}>
                    <strong>{selectedOrderItem.urun_adi}</strong>
                    <br />
                    için BOM tanımlı değil
                  </div>
                  <Button 
                    size="small" 
                    type="primary"
                    onClick={() => {
                      // Navigate to BOM management page
                      navigate('/production/bom');
                    }}
                  >
                    BOM Tanımla
                  </Button>
                </div>
              )}
            </>
          )}

          <Divider>Standart Operasyonlar</Divider>
          
          <div style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: 16 }}>
            {standardOperations.map((operation: any) => (
              <DraggableOperation
                key={operation.id}
                draggable
                onDragStart={(e) => handleDragStart(e, 'standard', operation)}
              >
                <strong>{operation.ad}</strong>
                <br />
                <Text type="secondary" style={{ fontSize: '11px' }}>{operation.aciklama}</Text>
                <br />
                <Tag size="small">{operation.tahmini_sure_birim} dk</Tag>
              </DraggableOperation>
            ))}
          </div>

          <Button 
            block 
            style={{ marginBottom: 16 }}
            onClick={() => setOperationDrawerOpen(true)}
          >
            <PlusOutlined /> Özel Operasyon
          </Button>

          <Button 
            block
            type={isConnecting ? "primary" : "default"}
            icon={<ArrowRightOutlined />}
            onClick={() => {
              setIsConnecting(!isConnecting);
              setConnectionStart(null);
            }}
            style={{ marginBottom: 16 }}
          >
            {isConnecting ? 'Bağlantı İptal' : 'Bağlantı Çiz'}
          </Button>

          {isConnecting && (
            <div style={{ marginTop: 8, padding: 8, background: '#e6f7ff', borderRadius: 4 }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                İki operasyonu sırayla tıklayarak bağlantı oluşturun
              </Text>
            </div>
          )}
        </LeftPanel>

        {/* Canvas */}
        <Canvas
          ref={canvasRef}
          onDragOver={handleCanvasDragOver}
          onDrop={handleCanvasDrop}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          <CanvasContent>
            {/* Connections */}
            <Connection>
              {connections.map((connection, index) => {
                const fromNode = nodes.find(n => n.id === connection.from);
                const toNode = nodes.find(n => n.id === connection.to);
                
                if (!fromNode || !toNode) return null;
                
                return (
                  <path
                    key={index}
                    d={getConnectionPath(fromNode, toNode)}
                    stroke="#1890ff"
                    strokeWidth="2"
                    fill="none"
                    markerEnd="url(#arrowhead)"
                  />
                );
              })}
              
              {/* Arrow marker */}
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon
                    points="0 0, 10 3.5, 0 7"
                    fill="#1890ff"
                  />
                </marker>
              </defs>
            </Connection>

            {/* Operation Nodes */}
            {nodes.map((node) => (
              <OperationNode
                key={node.id}
                x={node.x}
                y={node.y}
                selected={selectedNode === node.id}
                onMouseDown={(e) => handleNodeMouseDown(e, node.id)}
                onDoubleClick={() => handleNodeDoubleClick(node.id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <strong>{node.title}</strong>
                    {node.description && (
                      <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                        {node.description}
                      </div>
                    )}
                    <div style={{ marginTop: 8 }}>
                      <Tag size="small">
                        {node.duration} dk
                      </Tag>
                      {node.setupTime > 0 && (
                        <Tag size="small" color="orange">
                          Hzrl: {node.setupTime} dk
                        </Tag>
                      )}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                      {node.stationName}
                    </div>
                    {node.materials && node.materials.length > 0 && (
                      <div style={{ marginTop: 6 }}>
                        {node.materials.map((material, idx) => (
                          <Tag 
                            key={idx} 
                            size="small" 
                            color="green"
                            style={{ fontSize: '10px', marginBottom: '2px' }}
                          >
                            {material}
                          </Tag>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button
                    type="text"
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      deleteNode(node.id);
                    }}
                    style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  />
                </div>
              </OperationNode>
            ))}

            {/* Empty Canvas Message */}
            {nodes.length === 0 && (
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
                color: '#999'
              }}>
                <Title level={4} type="secondary">İş Akışı Tasarımına Başlayın</Title>
                <p>Sol panelden operasyonları bu alana sürükleyerek iş akışınızı tasarlayın</p>
              </div>
            )}
          </CanvasContent>
        </Canvas>
      </DesignerContainer>

      {/* Custom Operation Drawer */}
      <Drawer
        title="Özel Operasyon Ekle"
        placement="right"
        width={400}
        open={operationDrawerOpen}
        onClose={() => setOperationDrawerOpen(false)}
      >
        <Form
          layout="vertical"
          onFinish={(values) => {
            const newNode: OperationNodeType = {
              id: Date.now().toString(),
              x: 100,
              y: 100,
              title: values.title,
              description: values.description || '',
              duration: values.duration || 0,
              setupTime: values.setupTime || 0,
              stationId: values.stationId || 0,
              stationName: stations.find(s => s.id === values.stationId)?.ad || 'İstasyon Seçiniz',
              materials: []
            };
            
            setNodes(prev => [...prev, newNode]);
            setSelectedNode(newNode.id);
            setOperationDrawerOpen(false);
            message.success('Özel operasyon eklendi!');
          }}
        >
          <Form.Item
            label="Operasyon Adı"
            name="title"
            rules={[{ required: true, message: 'Operasyon adı gereklidir!' }]}
          >
            <Input placeholder="Operasyon adını girin" />
          </Form.Item>

          <Form.Item
            label="İstasyon"
            name="stationId"
            rules={[{ required: true, message: 'İstasyon seçimi gereklidir!' }]}
          >
            <Select placeholder="İstasyon seçin">
              {stations.map((station: any) => (
                <Option key={station.id} value={station.id}>
                  {station.ad}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Standart Süre (dakika)"
            name="duration"
          >
            <InputNumber 
              min={0} 
              step={0.5} 
              style={{ width: '100%' }}
              placeholder="İşlem süresini girin"
            />
          </Form.Item>

          <Form.Item
            label="Hazırlık Süresi (dakika)"
            name="setupTime"
          >
            <InputNumber 
              min={0} 
              step={0.5} 
              style={{ width: '100%' }}
              placeholder="Hazırlık süresini girin"
            />
          </Form.Item>

          <Form.Item
            label="Açıklama"
            name="description"
          >
            <Input.TextArea rows={3} placeholder="Operasyon hakkında açıklama..." />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Ekle
              </Button>
              <Button onClick={() => setOperationDrawerOpen(false)}>
                İptal
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>

      {/* Edit Node Drawer */}
      <Drawer
        title="Operasyon Düzenle"
        placement="right"
        width={400}
        open={editNodeDrawerOpen}
        onClose={() => setEditNodeDrawerOpen(false)}
      >
        {editingNode && (
          <Form
            layout="vertical"
            initialValues={{
              title: editingNode.title,
              description: editingNode.description,
              duration: editingNode.duration,
              setupTime: editingNode.setupTime,
              stationId: editingNode.stationId
            }}
            onFinish={(values) => {
              updateNode(editingNode.id, {
                title: values.title,
                description: values.description || '',
                duration: values.duration || 0,
                setupTime: values.setupTime || 0,
                stationId: values.stationId || 0,
                stationName: stations.find(s => s.id === values.stationId)?.ad || 'İstasyon Seçiniz'
              });
              setEditNodeDrawerOpen(false);
              message.success('Operasyon güncellendi!');
            }}
          >
            <Form.Item
              label="Operasyon Adı"
              name="title"
              rules={[{ required: true, message: 'Operasyon adı gereklidir!' }]}
            >
              <Input placeholder="Operasyon adını girin" />
            </Form.Item>

            <Form.Item
              label="İstasyon"
              name="stationId"
              rules={[{ required: true, message: 'İstasyon seçimi gereklidir!' }]}
            >
              <Select placeholder="İstasyon seçin">
                {stations.map((station: any) => (
                  <Option key={station.id} value={station.id}>
                    {station.ad}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              label="Standart Süre (dakika)"
              name="duration"
            >
              <InputNumber 
                min={0} 
                step={0.5} 
                style={{ width: '100%' }}
                placeholder="İşlem süresini girin"
              />
            </Form.Item>

            <Form.Item
              label="Hazırlık Süresi (dakika)"
              name="setupTime"
            >
              <InputNumber 
                min={0} 
                step={0.5} 
                style={{ width: '100%' }}
                placeholder="Hazırlık süresini girin"
              />
            </Form.Item>

            <Form.Item
              label="Açıklama"
              name="description"
            >
              <Input.TextArea rows={3} placeholder="Operasyon hakkında açıklama..." />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  Güncelle
                </Button>
                <Button onClick={() => setEditNodeDrawerOpen(false)}>
                  İptal
                </Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Drawer>

      {/* Settings Modal */}
      <Modal
        title="İş Akışı Ayarları"
        open={settingsModalOpen}
        onCancel={() => setSettingsModalOpen(false)}
        footer={[
          <Button key="cancel" onClick={() => setSettingsModalOpen(false)}>
            İptal
          </Button>,
          <Button 
            key="save" 
            type="primary" 
            onClick={() => {
              form.validateFields().then(values => {
                setWorkflowData(prev => ({ ...prev, ...values }));
                setSettingsModalOpen(false);
                message.success('Ayarlar güncellendi');
              });
            }}
          >
            Kaydet
          </Button>
        ]}
      >
        <Form form={form} layout="vertical" initialValues={workflowData}>
          <Form.Item
            label="İş Akışı Kodu"
            name="kod"
            rules={[{ required: true, message: 'İş akışı kodu gereklidir!' }]}
          >
            <Input placeholder="Örn: WF001" />
          </Form.Item>

          <Form.Item
            label="İş Akışı Adı"
            name="ad"
            rules={[{ required: true, message: 'İş akışı adı gereklidir!' }]}
          >
            <Input placeholder="İş akışı açıklayıcı adı" />
          </Form.Item>

          <Form.Item
            label="Ürün"
            name="urun"
            rules={[{ required: true, message: 'Ürün seçimi gereklidir!' }]}
          >
            <Select placeholder="İş akışının ait olduğu ürünü seçin">
              {products.map((product: any) => (
                <Option key={product.id} value={product.id}>
                  {product.ad} ({product.kod})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Akış Tipi"
            name="tip"
          >
            <Select>
              <Option value="seri">Seri İşlem</Option>
              <Option value="paralel">Paralel İşlem</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Açıklama"
            name="aciklama"
          >
            <Input.TextArea rows={3} placeholder="İş akışı hakkında açıklama..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WorkflowDesigner;