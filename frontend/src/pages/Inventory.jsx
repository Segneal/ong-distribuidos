import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { InventoryList } from '../components/inventory';

const Inventory = () => {
  const { user } = useAuth();

  // Verificar permisos (solo PRESIDENTE y VOCAL pueden acceder)
  if (!user || !['PRESIDENTE', 'VOCAL'].includes(user.role)) {
    return (
      <div className="access-denied">
        <h2>Acceso Denegado</h2>
        <p>No tiene permisos para acceder al inventario de donaciones.</p>
        <p>Solo los usuarios con rol de Presidente o Vocal pueden gestionar el inventario.</p>
      </div>
    );
  }

  return (
    <div className="inventory-page">
      <InventoryList />
    </div>
  );
};

export default Inventory;