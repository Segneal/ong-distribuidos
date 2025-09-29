import React, { useState } from 'react';
import ExternalEventList from '../components/events/ExternalEventList';
import VolunteerAdhesions from '../components/events/VolunteerAdhesions';
import '../components/network/Network.css';

const ExternalEvents = () => {
  const [activeTab, setActiveTab] = useState('events');

  return (
    <div className="external-events-page">
      <div className="page-header">
        <h1>Eventos de la Red de ONGs</h1>
        <p>Explore eventos de otras organizaciones y gestione sus adhesiones</p>
      </div>

      {/* Navegación por pestañas */}
      <div className="tabs-navigation">
        <button
          className={`tab-button ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          Eventos Disponibles
        </button>
        <button
          className={`tab-button ${activeTab === 'adhesions' ? 'active' : ''}`}
          onClick={() => setActiveTab('adhesions')}
        >
          Mis Adhesiones
        </button>
      </div>

      {/* Contenido de las pestañas */}
      <div className="tab-content">
        {activeTab === 'events' && (
          <div className="tab-panel">
            <ExternalEventList />
          </div>
        )}
        
        {activeTab === 'adhesions' && (
          <div className="tab-panel">
            <VolunteerAdhesions />
          </div>
        )}
      </div>
    </div>
  );
};

export default ExternalEvents;