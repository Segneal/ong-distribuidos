import React, { useState } from 'react';
import DonationOfferForm from '../components/network/DonationOfferForm';
import ExternalOffersList from '../components/network/ExternalOffersList';
import MyOffersList from '../components/network/MyOffersList';
import '../components/network/Network.css';

const DonationOffers = () => {
  const [activeTab, setActiveTab] = useState('external');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const handleCreateSuccess = () => {
    setShowCreateForm(false);
    // Cambiar a "Mis Ofertas" para ver la nueva oferta creada
    setActiveTab('my-offers');
  };

  const handleCreateCancel = () => {
    setShowCreateForm(false);
  };

  return (
    <div className="donation-offers-page">
      <div className="page-header">
        <h1>Ofertas de Donaciones</h1>
        <p>Explore ofertas disponibles y publique las suyas propias</p>
      </div>

      {!showCreateForm ? (
        <>
          {/* Navegación por pestañas */}
          <div className="tabs-navigation">
            <button
              className={`tab-button ${activeTab === 'external' ? 'active' : ''}`}
              onClick={() => setActiveTab('external')}
            >
              Ofertas Disponibles
            </button>
            <button
              className={`tab-button ${activeTab === 'my-offers' ? 'active' : ''}`}
              onClick={() => setActiveTab('my-offers')}
            >
              Mis Ofertas
            </button>
            <button
              className="btn btn-primary create-offer-btn"
              onClick={() => setShowCreateForm(true)}
            >
              + Nueva Oferta
            </button>
          </div>

          {/* Contenido de las pestañas */}
          <div className="tab-content">
            {activeTab === 'external' && (
              <div className="tab-panel">
                <ExternalOffersList />
              </div>
            )}
            {activeTab === 'my-offers' && (
              <div className="tab-panel">
                <MyOffersList />
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="create-form-container">
          <div className="form-header">
            <h2>Nueva Oferta de Donación</h2>
            <p>Publique donaciones de su inventario para que otras organizaciones puedan conocer su disponibilidad</p>
          </div>
          <DonationOfferForm 
            onSuccess={handleCreateSuccess}
            onCancel={handleCreateCancel}
          />
        </div>
      )}
    </div>
  );
};

export default DonationOffers;