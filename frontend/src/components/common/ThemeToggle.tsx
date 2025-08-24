import React from 'react';
import { Button, Tooltip } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useTheme } from '../../contexts/ThemeContext';
import styled from 'styled-components';

const ToggleButton = styled(Button)`
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .anticon {
    font-size: 18px;
  }
`;

const ThemeToggle: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <Tooltip title={isDark ? 'Light Mode' : 'Dark Mode'} placement="bottom">
      <ToggleButton
        type={isDark ? 'primary' : 'default'}
        icon={isDark ? <SunOutlined /> : <MoonOutlined />}
        onClick={toggleTheme}
        style={{
          backgroundColor: isDark ? '#1890ff' : '#fafafa',
          borderColor: isDark ? '#1890ff' : '#d9d9d9',
          color: isDark ? '#fff' : '#666',
        }}
      />
    </Tooltip>
  );
};

export default ThemeToggle;