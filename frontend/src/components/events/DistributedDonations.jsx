import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Events.css';

const DistributedDonations = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, hasPermission } = useAuth();

  const [event, setEvent] = useState(null);
  const [donations, setDonations] = useState([]);
  const [selectedDonations, setSelectedDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadEventAndDonations();
  }, [id]);

  const loadEventAndDonations = async () => {
    try {
      setLoading(true);
      
      // Load event details
      const eventResponse = await api.get(`/events/${id}`);
      const eventData = eventResponse.data.event;
      setEvent(eventData);

      // Check if event is in the past
      if (new Date(eventData.eventDate) >= new Date()) {
        setError('Solo se pueden registrar donaciones en eventos pasados');
        return;
      }

      // Load available donations
      const donationsResponse = await api.get('/inventory');
      const availableDonations = donationsResponse.data.donations?.filter(d => !d.deleted && d.quantity > 0) || [];
      setDonations(availableDonations);

      setError('');
    } catch (err) {
      setError('Error al cargar datos');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDonationChange = (donationId, quantity) => {
    setSelectedDonations(prev => {
      const existing = prev.find(d => d.donationId === donationId);
      if (existing) {
        if (quantity <= 0) {
          return prev.filter(d => d.donationId !== donationId);
        } else {
          return prev.map(d => 
            d.donationId === donationId 
              ? { ...d, quantity: parseInt(quantity) }
              : d
          );
        }
      } else if (quantity > 0) {
        return [...prev, { donationId, quantity: parseInt(quantity) }];
      }
      return prev;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (selectedDonations.length === 0) {
      setError('Seleccione al menos una donación para registrar');
      return;
    }

    // Validate quantities
    for (const selected of selectedDonations) {
      const donation = donations.find(d => d.id === selected.donationId);
      if (selected.quantity > donation.quantity) {
        setError(`La cantidad para "${donation.description}" no puede ser mayor a ${donation.quantity}`);
        return;
      }
    }

    try {
      setLoading(true);
      setError('');
      
      await api.post(`/events/${id}/distributed-donations`, {
        donations: selectedDonations
      });

      setSuccess('Donaciones registradas exitosamente');
      setTimeout(() => {
        navigate('/events');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al registrar donaciones');
      console.error('Error registering donations:', err);
    } finally {
      setLoading(false);
    }
  };

  const canRegisterDonations = hasPermission('events', 'update');

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryLabel = (category) => {
    const categories = {
      'ROPA': 'Ropa',
      'ALIMENTOS': 'Alimentos',
      'JUGUETES': 'Juguetes',
      'UTILES_ESCOLARES': 'Útiles Escolares'
    };
    return categories[category] || category;
  };

  if (!canRegisterDonations) {
    return (
      <div className="error-message">
        No tiene permisos para registrar donaciones repartidas
      </div>
    );
  }

  if (loading) {
    return <div className="loading">Cargando datos...</div>;
  }

  if (!event) {
    return <div className="error-message">Evento no encontrado</div>;
  }

  return (
    <div className="distributed-donations-container">
      <div className="form-header">
        <h2>Registrar Donaciones Repartidas</h2>
        <button 
          className="btn btn-secondary"
          onClick={() => navigate('/events')}
        >
          Volver a Eventos
        </button>
      </div>

      <div className="event-info">
        <h3>{event.name}</h3>
        <p className="event-date">{formatDate(event.eventDate)}</p>
        {event.description && <p className="event-description">{event.description}</p>}
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {!error && (
        <form onSubmit={handleSubmit} className="distributed-donations-form">
          <h4>Seleccionar Donaciones Repartidas</h4>
          
          {donations.length === 0 ? (
            <div className="no-donations">No hay donaciones disponibles en el inventario</div>
          ) : (
            <div className="donations-grid">
              {donations.map(donation => (
                <div key={donation.id} className="donation-item">
                  <div className="donation-info">
                    <h5>{donation.description}</h5>
                    <p className="donation-category">{getCategoryLabel(donation.category)}</p>
                    <p className="donation-available">Disponible: {donation.quantity}</p>
                  </div>
                  <div className="donation-input">
                    <label htmlFor={`quantity-${donation.id}`}>Cantidad repartida:</label>
                    <input
                      type="number"
                      id={`quantity-${donation.id}`}
                      min="0"
                      max={donation.quantity}
                      placeholder="0"
                      onChange={(e) => handleDonationChange(donation.id, e.target.value)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {selectedDonations.length > 0 && (
            <div className="selected-donations-summary">
              <h5>Resumen de donaciones a registrar:</h5>
              <ul>
                {selectedDonations.map(selected => {
                  const donation = donations.find(d => d.id === selected.donationId);
                  return (
                    <li key={selected.donationId}>
                      {donation.description}: {selected.quantity} unidades
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/events')}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || selectedDonations.length === 0}
            >
              {loading ? 'Registrando...' : 'Registrar Donaciones'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default DistributedDonations;