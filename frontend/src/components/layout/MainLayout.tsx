import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Avatar, Typography, Space } from 'antd';
import { 
  MenuFoldOutlined, 
  MenuUnfoldOutlined, 
  DashboardOutlined,
  ShoppingCartOutlined,
  ShoppingOutlined,
  BuildOutlined,
  BarChartOutlined,
  SettingOutlined,
  EditOutlined
} from '@ant-design/icons';
import { Outlet, useLocation, Link } from 'react-router-dom';
import styled from 'styled-components';
import ThemeToggle from '../common/ThemeToggle';
import MegaWorksLogo from '../../assets/MegaWorksBaslikLogo.jpeg';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
`;

const StyledHeader = styled(Header)`
  padding: 0 24px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const LogoImage = styled.img`
  height: 32px;
  width: auto;
  object-fit: contain;
`;

const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: <Link to="/">Ana Sayfa</Link>,
  },
  {
    key: '/dashboard',
    icon: <BarChartOutlined />,
    label: <Link to="/dashboard">Genel Dashboard</Link>,
  },
  {
    key: '/sales',
    icon: <ShoppingCartOutlined />,
    label: <Link to="/sales">Satış</Link>,
  },
  {
    key: 'procurement-group',
    icon: <ShoppingOutlined />,
    label: 'Satın Alma',
    children: [
      {
        key: '/procurement',
        label: <Link to="/procurement">Dashboard</Link>,
      },
      {
        key: 'procurement-orders',
        label: 'Satın Alma Siparişleri',
        children: [
          {
            key: '/procurement/orders',
            label: <Link to="/procurement/orders">Sipariş Listesi</Link>,
          },
          {
            key: '/procurement/orders/new',
            label: <Link to="/procurement/orders/new">Yeni Sipariş</Link>,
          },
          {
            key: '/procurement/orders/changes',
            label: <Link to="/procurement/orders/changes">Sipariş Değişiklikleri</Link>,
          },
          {
            key: '/procurement/orders/cancel',
            label: <Link to="/procurement/orders/cancel">Sipariş İptali</Link>,
          },
        ],
      },
      {
        key: '/procurement/suppliers',
        label: <Link to="/procurement/suppliers">Tedarikçiler</Link>,
      },
      {
        key: '/procurement/materials',
        label: <Link to="/procurement/materials">Malzemeler</Link>,
      },
      {
        key: '/procurement/reports',
        label: <Link to="/procurement/reports">Raporlar</Link>,
      },
    ],
  },
  {
    key: '/production',
    icon: <BuildOutlined />,
    label: <Link to="/production">Üretim</Link>,
  },
  {
    key: '/reports',
    icon: <BarChartOutlined />,
    label: <Link to="/reports">Raporlar</Link>,
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">Ayarlar</Link>,
  },
  {
    key: '/visual-editor',
    icon: <EditOutlined />,
    label: <Link to="/visual-editor">Görsel Editör</Link>,
  },
];

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [openKeys, setOpenKeys] = useState<string[]>([]);
  const location = useLocation();

  // Aktif menü anahtarlarını belirleme
  const getActiveKeys = () => {
    const path = location.pathname;
    const activeKeys = [path];
    
    // Ana grup anahtarlarını ekle
    if (path.startsWith('/procurement')) {
      activeKeys.push('procurement-group');
      if (path.includes('/orders')) {
        activeKeys.push('procurement-orders');
      }
    } else if (path.startsWith('/production')) {
      activeKeys.push('/production'); // Production tek menü item olduğu için
    }
    
    return activeKeys;
  };

  // Varsayılan açık menü anahtarları
  const getDefaultOpenKeys = () => {
    const path = location.pathname;
    const openKeys = [];
    
    if (path.startsWith('/procurement')) {
      openKeys.push('procurement-group');
      if (path.includes('/orders')) {
        openKeys.push('procurement-orders');
      }
    }
    // Production artık submenu olmadığı için hiçbir şey eklemeye gerek yok
    
    return openKeys;
  };

  // Sayfa başlığını belirleme
  const getPageTitle = () => {
    const path = location.pathname;
    
    // Recursive function to find menu item
    const findMenuItem = (items: any[], targetKey: string): any => {
      for (const item of items) {
        if (item.key === targetKey) {
          return item;
        }
        if (item.children) {
          const found = findMenuItem(item.children, targetKey);
          if (found) return found;
        }
      }
      return null;
    };

    const menuItem = findMenuItem(menuItems, path);
    if (menuItem?.label?.props?.children) {
      return menuItem.label.props.children;
    }

    // Fallback için özel durumlar
    const pageTitles: { [key: string]: string } = {
      '/': 'Ana Sayfa',
      '/dashboard': 'Genel Dashboard',
      '/sales': 'Satış Dashboard',
      '/sales/orders': 'Sipariş Listesi',
      '/sales/orders/new': 'Yeni Sipariş',
      '/sales/orders/changes': 'Sipariş Değişiklikleri',
      '/sales/orders/cancel': 'Sipariş İptali',
      '/sales/customers': 'Müşteriler',
      '/sales/reports': 'Satış Raporları',
      '/procurement': 'Satın Alma Dashboard',
      '/procurement/orders': 'Satın Alma Siparişleri',
      '/procurement/orders/new': 'Yeni Satın Alma Siparişi',
      '/procurement/orders/changes': 'Satın Alma Değişiklikleri',
      '/procurement/orders/cancel': 'Satın Alma İptali',
      '/procurement/suppliers': 'Tedarikçiler',
      '/procurement/materials': 'Malzemeler',
      '/procurement/reports': 'Satın Alma Raporları',
      '/production': 'Üretim Dashboard',
      '/production/work-orders': 'İş Emri Listesi',
      '/production/work-orders/new': 'Yeni İş Emri',
      '/production/work-orders/changes': 'İş Emri Değişiklikleri',
      '/production/work-orders/cancel': 'İş Emri İptali',
      '/production/stations': 'İş İstasyonları',
      '/production/bom': 'Reçeteler (BOM)',
      '/production/reports': 'Üretim Raporları',
      '/reports': 'Raporlar',
      '/settings': 'Ayarlar',
      '/visual-editor': 'Görsel Editör',
    };

    return pageTitles[path] || 'Dashboard';
  };

  // Sayfa değiştiğinde menü durumunu güncelle
  useEffect(() => {
    const defaultKeys = getDefaultOpenKeys();
    setOpenKeys(prevKeys => {
      // Mevcut açık anahtarları koru ve yenilerini ekle
      const newKeys = [...new Set([...prevKeys, ...defaultKeys])];
      return newKeys;
    });
  }, [location.pathname]);

  // Menü aç/kapat işlemi
  const onOpenChange = (keys: string[]) => {
    setOpenKeys(keys);
  };

  return (
    <StyledLayout>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        theme="light"
        style={{
          boxShadow: '2px 0 8px rgba(0,0,0,0.06)',
          zIndex: 1,
        }}
      >
        <LogoContainer style={{ 
          padding: '16px', 
          borderBottom: '1px solid #f0f0f0',
          justifyContent: collapsed ? 'center' : 'flex-start'
        }}>
          <LogoImage src={MegaWorksLogo} alt="MegaWorks Transformer" />
          {!collapsed && <Title level={5} style={{ margin: 0, color: '#1890ff' }}>Üretim Planlama</Title>}
        </LogoContainer>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={getActiveKeys()}
          openKeys={openKeys}
          onOpenChange={onOpenChange}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <StyledHeader>
          <Space>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              size="large"
            />
            <Title level={4} style={{ margin: 0, color: '#666' }}>
              {getPageTitle()}
            </Title>
          </Space>
          <Space size="large">
            <ThemeToggle />
            <Avatar size="large" style={{ backgroundColor: '#1890ff' }}>
              Admin
            </Avatar>
          </Space>
        </StyledHeader>
        <Content style={{ 
          margin: '24px', 
          padding: '24px',
          background: '#fff',
          borderRadius: '8px',
          minHeight: 'calc(100vh - 112px)',
        }}>
          <Outlet />
        </Content>
      </Layout>
    </StyledLayout>
  );
};

export default MainLayout;