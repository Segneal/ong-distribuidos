import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { eventsService } from '../../services/api';
import './Events.css';

const DistributedDonationsHistory = () => {
  const { id } = useParams();
  const { user, hasPermission } = useAuth();
  const [event, setEvent] = useState(null);
  const [distributedDonations, setDistributedDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadEventData();
  }, [id]);

  const loadEventData = async () => {
    try {
      setLoading(true);
      
      // Load event details
      const eventResponse = await eventsService.getEvent(id);
      setEvent(eventResponse.data.event);

      // Load distributed donations
      const donationsResponse = await eventsService.getDistributedDonations(id);
      setDistributedDonations(donationsResponse.data.distributedDonations || []);

      setError('');
    } catch (err) {
      setError('Error al cargar el historial de donaciones');
      console.error('Error loading distributed donations:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const canViewHistory = hasPermission('events', 'read');

  if (!canViewHistory) {
    return <div className="error-message">No tienes permisos para ver el historial de donaciones</div>;
  }

  if (loading) {
    return <div className="loading">Cargando historial de donaciones...</div>;
  }

  if (!event) {
    return <div className="error-message">Evento no encontrado</div>;
  }

  return (
    <div className="distributed-donations-history-container">
      <div className="form-header">
        <h2>Historial de Donaciones Distribuidas</h2>
        <button 
          className="btn btn-secondary"
          onClick={() => window.history.back()}
        >
          Volver
        </button>
      </div>

      <div className="event-info">
        <h3>{event.name}</h3>
        <p className="event-date">{formatDate(event.eventDate)}</p>
        {event.description && <p className="event-description">{event.description}</p>}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="donations-history-section">
        <h4>Donaciones Distribuidas ({distributedDonations.length})</h4>
        
        {distributedDonations.length === 0 ? (
          <div className="no-donations-history">
            No se han registrado donaciones distribuidas para este evento
          </div>
        ) : (
          <div className="donations-history-list">
            {distributedDonations.map(donation => (
              <div key={donation.id} className="donation-history-item">
                <div className="donation-main-info">
                  <h5 className="donation-description">{donation.donationDescription}</h5>
                  <div className="donation-quantity">
                    <span className="quantity-label">Cantidad distribuida:</span>
                    <span className="quantity-value">{donation.distributedQuantity}</span>
                  </div>
                </div>
                
                <div className="donation-meta-info">
                  <div className="registration-info">
                    <span className="meta-label">Registrado por:</span>
                    <span className="meta-value">
                      {donation.registeredByName || `Usuario ID ${donation.registeredBy}`}
                    </span>
                  </div>
                  <div className="registration-date">
                    <span className="meta-label">Fecha:</span>
                    <span className="meta-value">{formatDate(donation.registrationDate)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="summary-section">
        <div className="summary-card">
          <h5>Resumen</h5>
          <p>Total de registros: <strong>{distributedDonations.length}</strong></p>
          <p>Total de items distribuidos: <strong>
            {distributedDonations.reduce((total, donation) => total + donation.distributedQuantity, 0)}
          </strong></p>
        </div>
      </div>
    </div>
  );
};

export default DistributedDonationsHistory;