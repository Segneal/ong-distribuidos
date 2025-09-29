import React, { useState } from 'react';
import DonationRequestForm from '../components/network/DonationRequestForm';
import ExternalRequestsList from '../components/network/ExternalRequestsList';
import ActiveRequestsList from '../components/network/ActiveRequestsList';
import '../components/network/Network.css';

const DonationRequests = () => {
  const [activeTab, setActiveTab] = useState('external');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const handleCreateSuccess = () => {
    setShowCreateForm(false);
    // Cambiar a la pestaña de solicitudes activas para ver la nueva solicitud
    setActiveTab('active');
  };

  const handleCreateCancel = () => {
    setShowCreateForm(false);
  };

  return (
    <div className="donation-requests-page">
      <div className="page-header">
        <h1>Solicitudes de Donaciones</h1>
        <p>Gestione las solicitudes de donaciones de la red de ONGs</p>
      </div>

      {!showCreateForm ? (
        <>
          {/* Navegación por pestañas */}
          <div className="tabs-navigation">
            <button
              className={`tab-button ${activeTab === 'external' ? 'active' : ''}`}
              onClick={() => setActiveTab('external')}
            >
              Solicitudes Externas
            </button>
            <button
              className={`tab-button ${activeTab === 'active' ? 'active' : ''}`}
              onClick={() => setActiveTab('active')}
            >
              Mis Solicitudes
            </button>
            <button
              className="btn btn-primary create-request-btn"
              onClick={() => setShowCreateForm(true)}
            >
              + Nueva Solicitud
            </button>
          </div>

          {/* Contenido de las pestañas */}
          <div className="tab-content">
            {activeTab === 'external' && (
              <div className="tab-panel">
                <ExternalRequestsList />
              </div>
            )}
            
            {activeTab === 'active' && (
              <div className="tab-panel">
                <ActiveRequestsList />
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="create-form-container">
          <div className="form-header">
            <h2>Nueva Solicitud de Donación</h2>
            <p>Complete el formulario para solicitar donaciones a la red de ONGs</p>
          </div>
          <DonationRequestForm 
            onSuccess={handleCreateSuccess}
            onCancel={handleCreateCancel}
          />
        </div>
      )}
    </div>
  );
};

export default DonationRequests;