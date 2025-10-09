import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { messagingService } from '../../services/api';
import './Events.css';

const EventAdhesions = ({ eventId, eventName, onClose }) => {
  const { user } = useAuth();
  const [adhesions, setAdhesions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (eventId) {
      loadEventAdhesions();
    }
  }, [eventId]);

  const loadEventAdhesions = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await messagingService.getEventAdhesions(eventId);
      
      if (response.data.success) {
        setAdhesions(response.data.adhesions || []);
      } else {
        setError('Error al cargar adhesiones del evento');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || 'Error al cargar adhesiones';
      setError(errorMessage);
      console.error('Error loading event adhesions:', err);
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
      'PENDIENTE': { class: 'status-pending', text: 'Pendiente' },
      'CONFIRMADA': { class: 'status-confirmed', text: 'Confirmada' },
      'CANCELADA': { class: 'status-cancelled', text: 'Cancelada' }
    };
    
    const statusInfo = statusMap[status] || { class: 'status-unknown', text: status };
    
    return (
      <span className={`status-badge ${statusInfo.class}`}>
        {statusInfo.text}
      </span>
    );
  };

  const getVolunteerTypeBadge = (isExternal) => {
    return (
      <span className={`volunteer-type-badge ${isExternal ? 'external' : 'internal'}`}>
        {isExternal ? 'Voluntario Externo' : 'Voluntario Local'}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="modal-overlay">
        <div className="modal-content">
          <div className="loading">Cargando adhesiones...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Adhesiones al Evento: {eventName}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}

          <div className="adhesions-summary">
            <div className="summary-stats">
              <div className="stat-item">
                <span className="stat-number">{adhesions.length}</span>
                <span className="stat-label">Total Adhesiones</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {adhesions.filter(a => a.status === 'CONFIRMADA').length}
                </span>
                <span className="stat-label">Confirmadas</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {adhesions.filter(a => a.status === 'PENDIENTE').length}
                </span>
                <span className="stat-label">Pendientes</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {adhesions.filter(a => a.external_volunteer).length}
                </span>
                <span className="stat-label">Externos</span>
              </div>
            </div>
          </div>

          <div className="adhesions-list">
            {adhesions.length === 0 ? (
              <div className="no-adhesions">
                <p>No hay adhesiones para este evento.</p>
              </div>
            ) : (
              adhesions.map(adhesion => (
                <div key={adhesion.id} className="adhesion-item">
                  <div className="adhesion-info">
                    <div className="volunteer-header">
                      <h4>
                        {adhesion.volunteer_name} {adhesion.volunteer_surname}
                      </h4>
                      <div className="badges">
                        {getStatusBadge(adhesion.status)}
                        {getVolunteerTypeBadge(adhesion.external_volunteer)}
                      </div>
                    </div>
                    
                    <div className="volunteer-details">
                      <div className="detail-row">
                        <span className="detail-label">Email:</span>
                        <span className="detail-value">
                          {adhesion.volunteer_email || 'No especificado'}
                        </span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="detail-label">Teléfono:</span>
                        <span className="detail-value">
                          {adhesion.volunteer_phone || 'No especificado'}
                        </span>
                      </div>
                      
                      {adhesion.external_volunteer && (
                        <div className="detail-row">
                          <span className="detail-label">Organización:</span>
                          <span className="detail-value">
                            {adhesion.organization_id || 'No especificada'}
                          </span>
                        </div>
                      )}
                      
                      <div className="detail-row">
                        <span className="detail-label">Fecha de Adhesión:</span>
                        <span className="detail-value">
                          {formatDate(adhesion.adhesion_date)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="adhesion-actions">
                    {adhesion.status === 'PENDIENTE' && (
                      <div className="action-buttons">
                        <button 
                          className="btn btn-success btn-sm"
                          onClick={() => {
                            // TODO: Implement confirm adhesion
                            console.log('Confirming adhesion:', adhesion.id);
                          }}
                        >
                          Confirmar
                        </button>
                        <button 
                          className="btn btn-danger btn-sm"
                          onClick={() => {
                            // TODO: Implement reject adhesion
                            console.log('Rejecting adhesion:', adhesion.id);
                          }}
                        >
                          Rechazar
                        </button>
                      </div>
                    )}
                    
                    {adhesion.status === 'CONFIRMADA' && (
                      <div className="confirmed-indicator">
                        <i className="icon-check"></i>
                        Confirmada
                      </div>
                    )}
                    
                    {adhesion.status === 'CANCELADA' && (
                      <div className="cancelled-indicator">
                        <i className="icon-x"></i>
                        Cancelada
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cerrar
          </button>
          <button 
            className="btn btn-primary" 
            onClick={loadEventAdhesions}
          >
            Actualizar
          </button>
        </div>
      </div>
    </div>
  );
};

export default EventAdhesions;