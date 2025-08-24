import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.tsx';
import HomePage from './pages/HomePage.tsx';
import Dashboard from './pages/Dashboard.tsx';
import SimpleVisualEditor from './pages/SimpleVisualEditor.tsx';
import SalesDashboard from './pages/modules/SalesDashboard.tsx';
import ProcurementDashboard from './pages/modules/ProcurementDashboard.tsx';
import OrderList from './pages/sales/OrderList.tsx';
import OrderForm from './pages/sales/OrderForm.tsx';
import OrderDetail from './pages/sales/OrderDetail.tsx';
import OrderChanges from './pages/sales/OrderChanges.tsx';
import OrderCancel from './pages/sales/OrderCancel.tsx';
import './index.css';

// Placeholder components
const ProductionDashboard = () => <div>Üretim Dashboard'u yakında...</div>;
const ReportsDashboard = () => <div>Yönetim Raporları Dashboard'u yakında...</div>;
const Settings = () => <div>Ayarlar sayfası yakında...</div>;
const CustomerList = () => <div>Müşteri listesi yakında...</div>;
const SalesReports = () => <div>Satış raporları yakında...</div>;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<HomePage />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="sales" element={<SalesDashboard />} />
          <Route path="sales/orders" element={<OrderList />} />
          <Route path="sales/orders/:id" element={<OrderDetail />} />
          <Route path="sales/orders/new" element={<OrderForm />} />
          <Route path="sales/orders/:id/edit" element={<OrderForm />} />
          <Route path="sales/orders/changes" element={<OrderChanges />} />
          <Route path="sales/orders/cancel" element={<OrderCancel />} />
          <Route path="sales/customers" element={<CustomerList />} />
          <Route path="sales/customers/new" element={<CustomerList />} />
          <Route path="sales/reports" element={<SalesReports />} />
          <Route path="procurement" element={<ProcurementDashboard />} />
          <Route path="production" element={<ProductionDashboard />} />
          <Route path="reports" element={<ReportsDashboard />} />
          <Route path="settings" element={<Settings />} />
          <Route path="visual-editor" element={<SimpleVisualEditor />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
