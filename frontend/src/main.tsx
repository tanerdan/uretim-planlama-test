import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.tsx';
import HomePage from './pages/HomePage.tsx';
import Dashboard from './pages/Dashboard.tsx';
import SimpleVisualEditor from './pages/SimpleVisualEditor.tsx';
import SalesDashboard from './pages/modules/SalesDashboard.tsx';
import ProcurementDashboard from './pages/modules/ProcurementDashboard.tsx';
import ProductionDashboard from './pages/modules/ProductionDashboard.tsx';
import OrderList from './pages/sales/OrderList.tsx';
import OrderForm from './pages/sales/OrderForm.tsx';
import OrderDetail from './pages/sales/OrderDetail.tsx';
import OrderChanges from './pages/sales/OrderChanges.tsx';
import OrderCancel from './pages/sales/OrderCancel.tsx';

// Production pages
import StationManagement from './pages/production/StationManagement.tsx';
import MRPManagement from './pages/production/MRPManagement.tsx';
import WorkflowManagement from './pages/production/WorkflowManagement.tsx';
import WorkflowDesigner from './pages/production/WorkflowDesigner.tsx';
import WorkOrderManagement from './pages/production/WorkOrderManagement.tsx';
import BOMManagement from './pages/production/BOMManagement.tsx';
import './index.css';

// Placeholder components  
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
          <Route path="production/stations" element={<StationManagement />} />
          <Route path="production/mrp" element={<MRPManagement />} />
          <Route path="production/workflows" element={<WorkflowManagement />} />
          <Route path="production/workflows/new" element={<WorkflowDesigner />} />
          <Route path="production/workflows/:id/edit" element={<WorkflowDesigner />} />
          <Route path="production/work-orders" element={<WorkOrderManagement />} />
          <Route path="production/bom" element={<BOMManagement />} />
          <Route path="production/bom/:id" element={<BOMManagement />} />
          <Route path="reports" element={<ReportsDashboard />} />
          <Route path="settings" element={<Settings />} />
          <Route path="visual-editor" element={<SimpleVisualEditor />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
