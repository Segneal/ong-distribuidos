import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { messagingService } from '../../services/api';
import './Events.css';

const ExternalEventList = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showAdhesionModal, setShowAdhesionModal] = useState(false);
  const [submittingAdhesion, setSubmittingAdhesion] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterUpcoming, setFilterUpcoming] = useState(true);
  const [adhesionData, setAdhesionData] = useState({
    name: '',
    surname: '',
    phone: '',
    email: ''
  });

  useEffect(() => {
    loadExternalEvents();
    // Load user data for adhesion form
    if (user) {
      setAdhesionData({
        name: user.firstName || '',
        surname: user.lastName || '',
        phone: user.phone || '',
        email: user.email || ''
      });
    }
  }, [user, filterUpcoming]);

  const handleSearch = () => {
    loadExternalEvents();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const loadExternalEvents = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {
        activeOnly: true
      };
      
      if (searchTerm.trim()) {
        params.search = searchTerm.trim();
      }
      
      if (filterUpcoming) {
        params.upcomingOnly = true;
      }

      const response = await messagingService.getExternalEvents(params);
      
      if (response.data.success) {
        setEvents(response.data.events || []);
      } else {
        setError(response.data.error || 'Error al cargar eventos externos');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error al cargar eventos externos');
      console.error('Error loading external events:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdhesion = async (event) => {
    setSelectedEvent(event);
    setShowAdhesionModal(true);
  };

  const submitAdhesion = async () => {
    try {
      // Validate adhesion data
      if (!adhesionData.name || !adhesionData.surname || !adhesionData.email) {
        setError('Nombre, apellido y email son requeridos');
        return;
      }

      setSubmittingAdhesion(true);
      setError('');

      // Call messaging service to create adhesion
      const response = await messagingService.createEventAdhesion({
        eventId: selectedEvent.event_id,
        targetOrganization: selectedEvent.organization_id,
        volunteerData: {
          name: adhesionData.name,
          surname: adhesionData.surname,
          phone: adhesionData.phone,
          email: adhesionData.email
        }
      });

      if (response.data.success) {
        alert('Adhesión enviada exitosamente. La organización será notificada.');
        setShowAdhesionModal(false);
        setSelectedEvent(null);
        setError('');
      } else {
        setError(response.data.error || 'Error al enviar adhesión');
      }
      
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || 'Error al enviar adhesión';
      setError(errorMessage);
      console.error('Error submitting adhesion:', err);
    } finally {
      setSubmittingAdhesion(false);
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

  const isEventUpcoming = (eventDate) => {
    return new Date(eventDate) > new Date();
  };

  if (loading) {
    return <div className="loading">Cargando eventos externos...</div>;
  }

  const filteredEvents = events.filter(event => {
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      return (
        event.name.toLowerCase().includes(searchLower) ||
        event.description?.toLowerCase().includes(searchLower) ||
        event.organization_id.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  return (
    <div className="events-container">
      <div className="section-header">
        <h3>Eventos Disponibles de la Red</h3>
        <p>Explore eventos solidarios organizados por otras ONGs y adhiérase como voluntario.</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Filtros y búsqueda */}
      <div className="filters">
        <div className="filter-group search-group">
          <label htmlFor="search-input">Buscar eventos:</label>
          <input
            type="text"
            id="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Buscar por nombre, descripción u organización..."
          />
          <button 
            className="btn btn-secondary"
            onClick={handleSearch}
          >
            Buscar
          </button>
        </div>

        <div className="filter-group">
          <label>
            <input
              type="checkbox"
              checked={filterUpcoming}
              onChange={(e) => setFilterUpcoming(e.target.checked)}
            />
            Solo eventos próximos
          </label>
        </div>

        <button 
          className="btn btn-secondary"
          onClick={loadExternalEvents}
        >
          Actualizar
        </button>
      </div>

      <div className="events-list">
        {loading ? (
          <div className="loading">Cargando eventos externos...</div>
        ) : filteredEvents.length === 0 ? (
          <div className="no-events">
            {events.length === 0 ? (
              'No hay eventos externos disponibles en este momento'
            ) : (
              `No se encontraron eventos que coincidan con "${searchTerm}"`
            )}
          </div>
        ) : (
          <div className="events-grid">
            {filteredEvents.map(event => (
              <div key={`${event.organization_id}-${event.event_id}`} className="event-card external-event">
                <div className="event-header">
                  <h4>{event.name}</h4>
                  <div className="event-organization">
                    <span className="organization-badge">
                      {event.organization_id}
                    </span>
                  </div>
                </div>
                
                <div className="event-content">
                  <div className="event-date-info">
                    <strong>Fecha:</strong> {formatDate(event.event_date)}
                    {isEventUpcoming(event.event_date) ? (
                      <span className="upcoming-indicator"> (Próximo)</span>
                    ) : (
                      <span className="past-indicator"> (Finalizado)</span>
                    )}
                  </div>
                  
                  {event.description && (
                    <div className="event-description">
                      <strong>Descripción:</strong>
                      <p>{event.description}</p>
                    </div>
                  )}

                  <div className="event-meta">
                    <div className="meta-item">
                      <strong>ID del Evento:</strong> {event.event_id}
                    </div>
                    <div className="meta-item">
                      <strong>Publicado:</strong> {formatDate(event.timestamp)}
                    </div>
                  </div>
                </div>

                <div className="event-actions">
                  {isEventUpcoming(event.event_date) ? (
                    <button
                      className="btn btn-primary"
                      onClick={() => handleAdhesion(event)}
                    >
                      Adherirse como Voluntario
                    </button>
                  ) : (
                    <span className="event-status past">Evento Finalizado</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="section-info">
        <h4>Información:</h4>
        <ul>
          <li>Los eventos se actualizan automáticamente cuando otras ONGs los publican</li>
          <li>Puede buscar eventos por nombre, descripción u organización</li>
          <li>Use "Adherirse como Voluntario" para participar en eventos de otras organizaciones</li>
          <li>Sus adhesiones aparecerán en la pestaña "Mis Adhesiones"</li>
          <li>La organización organizadora será notificada de su adhesión</li>
        </ul>
      </div>

      {/* Modal para adhesión */}
      {showAdhesionModal && selectedEvent && (
        <div className="modal-overlay" onClick={() => setShowAdhesionModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Adherirse al Evento</h3>
              <button 
                className="modal-close"
                onClick={() => setShowAdhesionModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="event-summary">
                <h4>{selectedEvent.name}</h4>
                <p><strong>Organización:</strong> {selectedEvent.organization_id}</p>
                <p><strong>Fecha:</strong> {formatDate(selectedEvent.event_date)}</p>
                {selectedEvent.description && (
                  <p><strong>Descripción:</strong> {selectedEvent.description}</p>
                )}
              </div>

              <form className="adhesion-form">
                <h4>Datos del Voluntario</h4>
                
                <div className="form-group">
                  <label>Nombre *</label>
                  <input
                    type="text"
                    value={adhesionData.name}
                    onChange={(e) => setAdhesionData({...adhesionData, name: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Apellido *</label>
                  <input
                    type="text"
                    value={adhesionData.surname}
                    onChange={(e) => setAdhesionData({...adhesionData, surname: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Teléfono</label>
                  <input
                    type="tel"
                    value={adhesionData.phone}
                    onChange={(e) => setAdhesionData({...adhesionData, phone: e.target.value})}
                  />
                </div>

                <div className="form-group">
                  <label>Email *</label>
                  <input
                    type="email"
                    value={adhesionData.email}
                    onChange={(e) => setAdhesionData({...adhesionData, email: e.target.value})}
                    required
                  />
                </div>

                <div className="form-actions">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowAdhesionModal(false)}
                  >
                    Cancelar
                  </button>
                  <button
                    type="button"
                    className="btn btn-success"
                    onClick={submitAdhesion}
                    disabled={submittingAdhesion}
                  >
                    {submittingAdhesion ? 'Enviando...' : 'Enviar Adhesión'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExternalEventList;