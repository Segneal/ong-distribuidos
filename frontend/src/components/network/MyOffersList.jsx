import React, { useState, useEffect } from 'react';
import { messagingService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const MyOffersList = () => {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const categories = {
    'ROPA': 'Ropa',
    'ALIMENTOS': 'Alimentos', 
    'JUGUETES': 'Juguetes',
    'UTILES_ESCOLARES': 'Útiles Escolares'
  };

  useEffect(() => {
    fetchMyOffers();
  }, []);

  const fetchMyOffers = async () => {
    try {
      setLoading(true);
      const response = await messagingService.getMyOffers();
      
      if (response.data.success) {
        setOffers(response.data.offers || []);
      } else {
        setError('Error al cargar mis ofertas');
      }
    } catch (err) {
      console.error('Error al cargar mis ofertas:', err);
      setError('Error al cargar mis ofertas');
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivateOffer = async (offerId) => {
    if (!window.confirm('¿Está seguro de que desea desactivar esta oferta?')) {
      return;
    }

    try {
      const response = await messagingService.deactivateOffer(offerId);
      
      if (response.data.success) {
        fetchMyOffers(); // Refresh list
      } else {
        setError('Error al desactivar la oferta');
      }
    } catch (err) {
      console.error('Error al desactivar oferta:', err);
      setError('Error al desactivar la oferta');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="my-offers-container">
        <div className="loading">Cargando mis ofertas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-offers-container">
        <div className="error-message">{error}</div>
        <button className="btn btn-primary" onClick={fetchMyOffers}>
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="my-offers-container">
      <div className="section-header">
        <h3>Mis Ofertas de Donación</h3>
        <p className="section-description">
          Estas son las ofertas que has publicado en la red de ONGs.
        </p>
      </div>

      {offers.length === 0 ? (
        <div className="no-offers">
          <h4>No tienes ofertas publicadas</h4>
          <p>Cuando publiques ofertas de donación, aparecerán aquí.</p>
        </div>
      ) : (
        <div className="offers-list">
          {offers.map((offer) => (
            <div key={offer.id} className={`offer-card ${!offer.activa ? 'inactive' : ''}`}>
              <div className="offer-header">
                <div className="offer-info">
                  <h4>Oferta #{offer.oferta_id}</h4>
                  <span className={`status-badge ${offer.activa ? 'active' : 'inactive'}`}>
                    {offer.activa ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
                <div className="offer-date">
                  {formatDate(offer.fecha_creacion)}
                </div>
              </div>

              <div className="offer-donations">
                <h5>Donaciones ofrecidas:</h5>
                <div className="donations-grid">
                  {offer.donaciones && offer.donaciones.map((donation, index) => (
                    <div key={index} className="donation-item">
                      <div className="donation-category">
                        {categories[donation.category] || donation.categoria || donation.category}
                      </div>
                      <div className="donation-description">
                        {donation.description || donation.descripcion}
                      </div>
                      <div className="donation-quantity">
                        Cantidad: {donation.quantity || donation.cantidad}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="offer-actions">
                {offer.activa && (
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDeactivateOffer(offer.oferta_id)}
                  >
                    Desactivar Oferta
                  </button>
                )}
                <div className="offer-stats">
                  <small className="text-muted">
                    Publicada el {formatDate(offer.fecha_creacion)}
                  </small>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="offers-info">
        <h4>Información sobre las ofertas:</h4>
        <ul>
          <li>Las ofertas activas son visibles para todas las organizaciones de la red</li>
          <li>Puedes desactivar una oferta en cualquier momento</li>
          <li>Las ofertas desactivadas no aparecen en la red pero se mantienen en tu historial</li>
          <li>Cuando otra organización solicite tus donaciones, recibirás una notificación</li>
        </ul>
      </div>

      <style jsx>{`
        .my-offers-container {
          padding: 20px;
        }
        
        .offer-card {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
          background: white;
        }
        
        .offer-card.inactive {
          opacity: 0.7;
          background: #f8f9fa;
        }
        
        .offer-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }
        
        .offer-info h4 {
          margin: 0;
          color: #333;
        }
        
        .status-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: bold;
        }
        
        .status-badge.active {
          background: #d4edda;
          color: #155724;
        }
        
        .status-badge.inactive {
          background: #f8d7da;
          color: #721c24;
        }
        
        .donations-grid {
          display: grid;
          gap: 10px;
          margin-top: 10px;
        }
        
        .donation-item {
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 12px;
          background: #f8f9fa;
        }
        
        .donation-category {
          font-weight: bold;
          color: #007bff;
          margin-bottom: 5px;
        }
        
        .donation-description {
          margin-bottom: 5px;
        }
        
        .donation-quantity {
          font-size: 14px;
          color: #666;
        }
        
        .offer-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 15px;
          padding-top: 15px;
          border-top: 1px solid #eee;
        }
        
        .no-offers {
          text-align: center;
          padding: 40px;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default MyOffersList;