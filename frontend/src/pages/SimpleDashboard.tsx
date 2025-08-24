import React, { useState } from 'react';
import { Card, Typography, Row, Col, Button, message, Space } from 'antd';
import { ApiOutlined, CheckCircleOutlined } from '@ant-design/icons';

const { Title } = Typography;

const SimpleDashboard: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<string>('Henüz test edilmedi');
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/');
      if (response.ok) {
        const data = await response.json();
        setApiStatus('✅ API Bağlantısı Başarılı');
        message.success('Backend API\'ye bağlandı!');
        console.log('API Response:', data);
      } else {
        setApiStatus('❌ API Bağlantı Hatası');
        message.error('API bağlantısı başarısız');
      }
    } catch (error) {
      setApiStatus('❌ Backend Sunucusuna Erişilemiyor');
      message.error('Backend sunucusuna erişilemiyor');
      console.error('API Error:', error);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>Üretim Planlama Dashboard</Title>
      
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Title level={4}>Test Kart 1</Title>
            <p>Bu kart çalışıyor</p>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={4}>Test Kart 2</Title>
            <p>Backend bağlantısı test edilecek</p>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={4}>Test Kart 3</Title>
            <p>API çağrıları yakında</p>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={4}>Test Kart 4</Title>
            <p>Herşey hazır!</p>
          </Card>
        </Col>
      </Row>
      
      <div style={{ marginTop: '24px' }}>
        <Card>
          <Title level={3}>Sistem Durumu</Title>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <ul>
              <li>✅ React Frontend Çalışıyor</li>
              <li>✅ Ant Design Yüklü</li>
              <li>✅ TypeScript Aktif</li>
              <li>{apiStatus}</li>
            </ul>
            
            <Space>
              <Button 
                type="primary" 
                icon={<ApiOutlined />} 
                onClick={testAPI}
                loading={loading}
              >
                API Bağlantısını Test Et
              </Button>
              
              <Button 
                type="dashed" 
                icon={<CheckCircleOutlined />}
                onClick={() => window.open('http://localhost:8000/api/', '_blank')}
              >
                Backend API'yi Tarayıcıda Aç
              </Button>
            </Space>
          </Space>
        </Card>
      </div>
    </div>
  );
};

export default SimpleDashboard;