import React, { useState, useEffect } from 'react';
import { messagingService, eventsService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const EventAdhesionManager = () => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [adhesions, setAdhesions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingAdhesions, setLoadingAdhesions] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [processingAdhesion, setProcessingAdhesion] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    loadOrganizationEvents();
  }, []);

  const loadOrganizationEvents = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Cargar eventos de la organización
      const response = await eventsService.getEvents({ includePastEvents: false });
      
      if (response.data.success) {
        setEvents(response.data.events || []);
      } else {
        setError('Error al cargar eventos de la organización');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error al cargar eventos');
      console.error('Error loading organization events:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadEventAdhesions = async (eventId) => {
    try {
      setLoadingAdhesions(true);
      setError('');
      
      const response = await messagingService.getEventAdhesions(eventId);
      
      if (response.data.success) {
        setAdhesions(response.data.adhesions || []);
      } else {
        setError('Error al cargar adhesiones del evento');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error al cargar adhesiones');
      console.error('Error loading event adhesions:', err);
    } finally {
      setLoadingAdhesions(false);
    }
  };

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
    loadEventAdhesions(event.id);
  };

  const handleApproveAdhesion = async (adhesionId) => {
    try {
      setProcessingAdhesion(true);
      setError('');
      setSuccess('');
      
      const response = await messagingService.approveEventAdhesion(adhesionId);
      
      if (response.data.success) {
        setSuccess('Adhesión aprobada exitosamente');
        // Recargar las adhesiones para mostrar el cambio de estado
        if (selectedEvent) {
          loadEventAdhesions(selectedEvent.id);
        }
        
        // Limpiar mensaje de éxito después de 3 segundos
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(response.data.error || 'Error al aprobar la adhesión');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error al aprobar la adhesión');
      console.error('Error approving adhesion:', err);
    } finally {
      setProcessingAdhesion(false);
    }
  };

  const handleRejectAdhesion = async (adhesionId) => {
    const reason = prompt('¿Motivo del rechazo? (opcional)');
    
    try {
      setProcessingAdhesion(true);
      setError('');
      setSuccess('');
      
      const response = await messagingService.rejectEventAdhesion(adhesionId, reason);
      
      if (response.data.success) {
        setSuccess('Adhesión rechazada exitosamente');
        // Recargar las adhesiones para mostrar el cambio de estado
        if (selectedEvent) {
          loadEventAdhesions(selectedEvent.id);
        }
        
        // Limpiar mensaje de éxito después de 3 segundos
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(response.data.error || 'Error al rechazar la adhesión');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error al rechazar la adhesión');
      console.error('Error rejecting adhesion:', err);
    } finally {
      setProcessingAdhesion(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'PENDIENTE': { class: 'status-pending', text: 'Pendiente' },
      'CONFIRMADA': { class: 'status-confirmed', text: 'Confirmada' },
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

  const getVolunteerTypeBadge = (isExternal) => {
    return (
      <span className={`volunteer-type-badge ${isExternal ? 'external' : 'internal'}`}>
        {isExternal ? 'Voluntario Externo' : 'Voluntario Local'}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="adhesion-manager-container">
        <div className="loading">Cargando eventos...</div>
      </div>
    );
  }

  return (
    <div className="adhesion-manager-container">
      <div className="section-header">
        <h3>Gestión de Adhesiones a Eventos</h3>
        <p>Administre las adhesiones de voluntarios externos a los eventos de su organización.</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="manager-layout">
        {/* Lista de eventos */}
        <div className="events-sidebar">
          <h4>Eventos de la Organización</h4>
          {events.length === 0 ? (
            <div className="no-events">
              No hay eventos disponibles
            </div>
          ) : (
            <div className="events-list">
              {events.map(event => (
                <div
                  key={event.id}
                  className={`event-item ${selectedEvent?.id === event.id ? 'selected' : ''}`}
                  onClick={() => handleEventSelect(event)}
                >
                  <div className="event-name">{event.name}</div>
                  <div className="event-date">{formatDate(event.date)}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Adhesiones del evento seleccionado */}
        <div className="adhesions-content">
          {!selectedEvent ? (
            <div className="no-selection">
              <p>Seleccione un evento para ver sus adhesiones</p>
            </div>
          ) : (
            <>
              <div className="event-info">
                <h4>{selectedEvent.name}</h4>
                <p><strong>Fecha:</strong> {formatDate(selectedEvent.date)}</p>
                {selectedEvent.description && (
                  <p><strong>Descripción:</strong> {selectedEvent.description}</p>
                )}
              </div>

              {loadingAdhesions ? (
                <div className="loading">Cargando adhesiones...</div>
              ) : (
                <>
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
                          {adhesions.filter(a => a.status === 'RECHAZADA').length}
                        </span>
                        <span className="stat-label">Rechazadas</span>
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
                              <h5>
                                {adhesion.volunteer_name} {adhesion.volunteer_surname}
                              </h5>
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
                                  onClick={() => handleApproveAdhesion(adhesion.adhesion_id)}
                                  disabled={loadingAdhesions || processingAdhesion}
                                >
                                  {processingAdhesion ? 'Procesando...' : 'Aprobar'}
                                </button>
                                <button 
                                  className="btn btn-danger btn-sm"
                                  onClick={() => handleRejectAdhesion(adhesion.adhesion_id)}
                                  disabled={loadingAdhesions || processingAdhesion}
                                >
                                  {processingAdhesion ? 'Procesando...' : 'Rechazar'}
                                </button>
                              </div>
                            )}
                            
                            {adhesion.status === 'CONFIRMADA' && (
                              <div className="confirmed-indicator">
                                ✓ Confirmada
                              </div>
                            )}
                            
                            {adhesion.status === 'CANCELADA' && (
                              <div className="cancelled-indicator">
                                ✗ Cancelada
                              </div>
                            )}
                            
                            {adhesion.status === 'RECHAZADA' && (
                              <div className="rejected-indicator">
                                ✗ Rechazada
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>

      <div className="section-info">
        <h4>Información:</h4>
        <ul>
          <li>Aquí puede ver todas las adhesiones de voluntarios externos a sus eventos</li>
          <li>Los voluntarios externos son de otras organizaciones de la red</li>
          <li>Puede confirmar o rechazar adhesiones pendientes</li>
          <li>Las confirmaciones se notifican automáticamente al voluntario</li>
        </ul>
      </div>
    </div>
  );
};

export default EventAdhesionManager;