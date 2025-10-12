import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { messagingService } from '../../services/api';
import './Events.css';

const VolunteerAdhesions = () => {
  const { user } = useAuth();
  const [adhesions, setAdhesions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      loadVolunteerAdhesions();
    }
  }, [user]);

  const loadVolunteerAdhesions = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await messagingService.getVolunteerAdhesions();
      
      if (response.data.success) {
        setAdhesions(response.data.adhesions || []);
      } else {
        setError('Error al cargar adhesiones');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || 'Error al cargar adhesiones';
      setError(errorMessage);
      console.error('Error loading volunteer adhesions:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No especificada';
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'PENDIENTE': { class: 'status-pending', text: 'Pendiente de Aprobación' },
      'CONFIRMADA': { class: 'status-confirmed', text: 'Aprobada' },
      'CANCELADA': { class: 'status-cancelled', text: 'Cancelada' },
      'RECHAZADA': { class: 'status-rejected', text: 'Rechazada' }
    };
    
    const statusInfo = statusMap[status] || { class: 'status-unknown', text: status };
    
    return (
      <span className={`status-badge ${statusInfo.class}`}>
        {statusInfo.text}
      </span>
    );
  };

  const isEventUpcoming = (eventDate) => {
    if (!eventDate) return false;
    return new Date(eventDate) > new Date();
  };

  if (loading) {
    return <div className="loading">Cargando adhesiones...</div>;
  }

  return (
    <div className="adhesions-container">
      <div className="adhesions-header">
        <h2>Mis Adhesiones a Eventos</h2>
        <button 
          className="btn btn-secondary"
          onClick={loadVolunteerAdhesions}
        >
          Actualizar
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="adhesions-info">
        <p>Aquí puedes ver todos los eventos externos a los que te has adherido como voluntario.</p>
      </div>

      <div className="adhesions-list">
        {adhesions.length === 0 ? (
          <div className="no-adhesions">
            <p>No tienes adhesiones a eventos externos.</p>
            <p>Visita la sección "Eventos de la Red" para adherirte a eventos de otras organizaciones.</p>
          </div>
        ) : (
          adhesions.map(adhesion => (
            <div key={adhesion.id} className="adhesion-card">
              <div className="adhesion-header">
                <h3>{adhesion.event_name}</h3>
                {getStatusBadge(adhesion.status)}
              </div>
              
              <div className="adhesion-details">
                <div className="detail-row">
                  <span className="detail-label">Organización:</span>
                  <span className="detail-value">{adhesion.organization_id}</span>
                </div>
                
                <div className="detail-row">
                  <span className="detail-label">Fecha del Evento:</span>
                  <span className="detail-value">
                    {formatDate(adhesion.event_date)}
                    {isEventUpcoming(adhesion.event_date) ? (
                      <span className="upcoming-indicator"> (Próximo)</span>
                    ) : (
                      <span className="past-indicator"> (Finalizado)</span>
                    )}
                  </span>
                </div>
                
                <div className="detail-row">
                  <span className="detail-label">Fecha de Adhesión:</span>
                  <span className="detail-value">{formatDate(adhesion.adhesion_date)}</span>
                </div>
                
                {adhesion.event_description && (
                  <div className="detail-row">
                    <span className="detail-label">Descripción:</span>
                    <span className="detail-value">{adhesion.event_description}</span>
                  </div>
                )}
              </div>

              <div className="adhesion-actions">
                {adhesion.status === 'PENDIENTE' && isEventUpcoming(adhesion.event_date) && (
                  <div className="pending-message">
                    <i className="icon-clock"></i>
                    Esperando confirmación de la organización
                  </div>
                )}
                
                {adhesion.status === 'CONFIRMADA' && isEventUpcoming(adhesion.event_date) && (
                  <div className="confirmed-message">
                    <i className="icon-check"></i>
                    Adhesión confirmada - ¡Nos vemos en el evento!
                  </div>
                )}
                
                {adhesion.status === 'CANCELADA' && (
                  <div className="cancelled-message">
                    <i className="icon-x"></i>
                    Adhesión cancelada
                  </div>
                )}
                
                {adhesion.status === 'RECHAZADA' && (
                  <div className="rejected-message">
                    <i className="icon-x"></i>
                    Adhesión rechazada por la organización
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default VolunteerAdhesions;