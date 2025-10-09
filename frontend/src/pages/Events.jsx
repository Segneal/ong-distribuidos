import React, { useState } from 'react';
import EventList from '../components/events/EventList';
import EventAdhesionManager from '../components/network/EventAdhesionManager';
import { useAuth } from '../contexts/AuthContext';
import '../components/network/Network.css';

const Events = () => {
  const [activeTab, setActiveTab] = useState('events');
  const { user, hasPermission } = useAuth();

  // Solo mostrar pestañas si el usuario tiene permisos de administración
  const showTabs = hasPermission('events', 'write');

  if (!showTabs) {
    return <EventList />;
  }

  return (
    <div className="events-page">
      <div className="page-header">
        <h1>Gestión de Eventos</h1>
        <p>Administre los eventos de su organización y las adhesiones de voluntarios</p>
      </div>

      {/* Navegación por pestañas */}
      <div className="tabs-navigation">
        <button
          className={`tab-button ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          Eventos
        </button>
        <button
          className={`tab-button ${activeTab === 'adhesions' ? 'active' : ''}`}
          onClick={() => setActiveTab('adhesions')}
        >
          Adhesiones de Red
        </button>
      </div>

      {/* Contenido de las pestañas */}
      <div className="tab-content">
        {activeTab === 'events' && (
          <div className="tab-panel">
            <EventList />
          </div>
        )}
        
        {activeTab === 'adhesions' && (
          <div className="tab-panel">
            <EventAdhesionManager />
          </div>
        )}
      </div>
    </div>
  );
};

export default Events;