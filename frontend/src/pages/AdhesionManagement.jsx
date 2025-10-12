import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import EventAdhesionManager from '../components/network/EventAdhesionManager';
import VolunteerAdhesions from '../components/events/VolunteerAdhesions';
import '../components/network/Network.css';
import '../components/adhesions/Adhesions.css';

const AdhesionManagement = () => {
  const { user, hasPermission } = useAuth();
  const [activeTab, setActiveTab] = useState('manage');

  const tabs = [
    {
      id: 'manage',
      label: 'Gestionar Adhesiones',
      icon: '👥',
      description: 'Administre las adhesiones a eventos de su organización',
      component: EventAdhesionManager,
      roles: ['PRESIDENTE', 'COORDINADOR', 'VOCAL'],
      permission: 'events'
    },
    {
      id: 'my-adhesions',
      label: 'Mis Adhesiones',
      icon: '📝',
      description: 'Vea sus adhesiones a eventos externos',
      component: VolunteerAdhesions,
      roles: ['PRESIDENTE', 'COORDINADOR', 'VOCAL', 'VOLUNTARIO'],
      permission: 'events'
    }
  ];

  const canAccessTab = (tab) => {
    return tab.roles.includes(user?.role) && hasPermission(tab.permission, 'read');
  };

  const availableTabs = tabs.filter(canAccessTab);

  // Si no hay tabs disponibles, mostrar mensaje
  if (availableTabs.length === 0) {
    return (
      <div className="adhesion-management-page">
        <div className="page-header">
          <h1>Gestión de Adhesiones</h1>
          <p>No tiene permisos para acceder a esta funcionalidad</p>
        </div>
      </div>
    );
  }

  // Si solo hay un tab disponible, mostrarlo directamente
  if (availableTabs.length === 1) {
    const singleTab = availableTabs[0];
    const Component = singleTab.component;
    
    return (
      <div className="adhesion-management-page">
        <div className="page-header">
          <h1>{singleTab.label}</h1>
          <p>{singleTab.description}</p>
        </div>
        <div className="page-content">
          <Component />
        </div>
      </div>
    );
  }

  // Si hay múltiples tabs, mostrar navegación por tabs
  const activeTabData = availableTabs.find(tab => tab.id === activeTab) || availableTabs[0];
  const Component = activeTabData.component;

  return (
    <div className="adhesion-management-page">
      <div className="page-header">
        <h1>Gestión de Adhesiones</h1>
        <p>Administre las adhesiones a eventos y vea su participación en la red</p>
      </div>

      <div className="tabs-container">
        <div className="tabs-nav">
          {availableTabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="tab-content">
          <div className="tab-description">
            <p>{activeTabData.description}</p>
          </div>
          <Component />
        </div>
      </div>

      <div className="adhesion-info">
        <div className="info-section">
          <h3>Información sobre Adhesiones</h3>
          <div className="info-grid">
            <div className="info-item">
              <div className="info-icon">🤝</div>
              <div className="info-content">
                <h4>Adhesiones Externas</h4>
                <p>Los voluntarios de otras organizaciones pueden adherirse a sus eventos públicos</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-icon">✅</div>
              <div className="info-content">
                <h4>Proceso de Aprobación</h4>
                <p>Todas las adhesiones requieren aprobación del coordinador o presidente del evento</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-icon">🔔</div>
              <div className="info-content">
                <h4>Notificaciones</h4>
                <p>Reciba notificaciones automáticas cuando haya nuevas adhesiones o cambios de estado</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-icon">📊</div>
              <div className="info-content">
                <h4>Seguimiento</h4>
                <p>Mantenga un registro completo de todas las adhesiones y su estado</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="adhesion-states-guide">
        <h3>Estados de las Adhesiones</h3>
        <div className="states-grid">
          <div className="state-item">
            <span className="status-badge status-pending">Pendiente</span>
            <p>La adhesión está esperando aprobación del organizador</p>
          </div>
          <div className="state-item">
            <span className="status-badge status-confirmed">Confirmada</span>
            <p>La adhesión ha sido aprobada y el voluntario puede participar</p>
          </div>
          <div className="state-item">
            <span className="status-badge status-rejected">Rechazada</span>
            <p>La adhesión ha sido rechazada por el organizador</p>
          </div>
          <div className="state-item">
            <span className="status-badge status-cancelled">Cancelada</span>
            <p>La adhesión ha sido cancelada por el voluntario</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdhesionManagement;