import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../components/network/Network.css';

const Network = () => {
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  const networkFeatures = [
    {
      title: 'Solicitudes de Donaciones',
      description: 'Publique solicitudes de donaciones y vea las necesidades de otras organizaciones',
      icon: '📋',
      path: '/donation-requests',
      permission: 'inventory',
      color: '#3498db'
    },
    {
      title: 'Transferencias',
      description: 'Transfiera donaciones directamente a organizaciones que las necesitan',
      icon: '🔄',
      path: '/donation-transfers',
      permission: 'inventory',
      color: '#e74c3c'
    },
    {
      title: 'Ofertas de Donaciones',
      description: 'Publique donaciones disponibles y explore ofertas de otras ONGs',
      icon: '🎁',
      path: '/donation-offers',
      permission: 'inventory',
      color: '#f39c12'
    },
    {
      title: 'Eventos Solidarios',
      description: 'Descubra eventos de otras organizaciones y permita adhesiones a los suyos',
      icon: '🤝',
      path: '/external-events',
      permission: 'events',
      color: '#9b59b6'
    },
    {
      title: 'Gestión de Adhesiones',
      description: 'Administre las adhesiones a sus eventos y vea sus participaciones externas',
      icon: '👥',
      path: '/adhesion-management',
      permission: 'events',
      color: '#2ecc71'
    }
  ];

  const handleFeatureClick = (feature) => {
    if (hasPermission(feature.permission, 'read')) {
      navigate(feature.path);
    }
  };

  return (
    <div className="network-page">
      <div className="page-header">
        <h1>Red de ONGs</h1>
        <p>Conecte con otras organizaciones para maximizar el impacto social</p>
      </div>

      <div className="network-stats">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">🌐</div>
            <div className="stat-content">
              <h3>Red Colaborativa</h3>
              <p>Conectado con organizaciones de toda la región</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🤲</div>
            <div className="stat-content">
              <h3>Donaciones Compartidas</h3>
              <p>Optimice la distribución de recursos</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>Voluntarios Unidos</h3>
              <p>Amplíe el alcance de sus eventos</p>
            </div>
          </div>
        </div>
      </div>


    </div>
  );
};

export default Network;