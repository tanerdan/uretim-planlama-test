import React from 'react';
import { Card, Typography, Button } from 'antd';
import { EditOutlined } from '@ant-design/icons';

const { Title } = Typography;

const SimpleVisualEditor: React.FC = () => {
  return (
    <div>
      <Title level={2}>Görsel Editör</Title>
      <Card>
        <p>Görsel editör yakında eklenecek...</p>
        <Button type="primary" icon={<EditOutlined />}>
          Editöre Git
        </Button>
      </Card>
    </div>
  );
};

export default SimpleVisualEditor;