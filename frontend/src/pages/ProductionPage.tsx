import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProductionDashboard from './modules/ProductionDashboard';

const ProductionPage: React.FC = () => {
  return (
    <Routes>
      <Route index element={<ProductionDashboard />} />
    </Routes>
  );
};

export default ProductionPage;