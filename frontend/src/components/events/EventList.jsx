import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api, { eventsService } from '../../services/api';
import './Events.css';

const EventList = () => {
  const { user, hasPermission } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [includePastEvents, setIncludePastEvents] = useState(() => {
    const saved = localStorage.getItem('includePastEvents');
    return saved ? JSON.parse(saved) : false;
  });
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showParticipants, setShowParticipants] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [userParticipations, setUserParticipations] = useState({});

  useEffect(() => {
    loadEvents();
  }, [includePastEvents]);

  useEffect(() => {
    localStorage.setItem('includePastEvents', JSON.stringify(includePastEvents));
  }, [includePastEvents]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      
      const response = await eventsService.getEvents({ includePastEvents });
      const eventsData = response.data.events || [];
      setEvents(eventsData);
      
      // Load participation status for each event
      await loadUserParticipations(eventsData);
      
      setError('');
    } catch (err) {
      setError('Error al cargar eventos');
      console.error('Error loading events:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUserParticipations = async (eventsData) => {
    try {
      const participations = {};
      
      for (const event of eventsData) {
        try {
          const response = await api.get(`/events/${event.id}/participants`);
          const eventParticipants = response.data.participants || [];
          participations[event.id] = eventParticipants.some(p => p.userId === user.id);
        } catch (err) {
          console.error(`Error loading participants for event ${event.id}:`, err);
          participations[event.id] = false;
        }
      }
      
      setUserParticipations(participations);
    } catch (err) {
      console.error('Error loading user participations:', err);
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (!window.confirm('¿Está seguro de que desea eliminar este evento?')) {
      return;
    }

    try {
      await api.delete(`/events/${eventId}`);
      setEvents(events.filter(event => event.id !== eventId));
    } catch (err) {
      setError('Error al eliminar evento');
      console.error('Error deleting event:', err);
    }
  };

  const handleJoinEvent = async (eventId) => {
    try {
      await api.post(`/events/${eventId}/participants`, {
        userId: user.id
      });
      // Update local state immediately
      setUserParticipations(prev => ({
        ...prev,
        [eventId]: true
      }));
    } catch (err) {
      setError('Error al unirse al evento');
      console.error('Error joining event:', err);
    }
  };

  const handleLeaveEvent = async (eventId) => {
    try {
      await api.delete(`/events/${eventId}/participants/${user.id}`);
      // Update local state immediately
      setUserParticipations(prev => ({
        ...prev,
        [eventId]: false
      }));
    } catch (err) {
      setError('Error al salir del evento');
      console.error('Error leaving event:', err);
    }
  };

  const loadParticipants = async (eventId) => {
    try {
      const response = await api.get(`/events/${eventId}/participants`);
      setParticipants(response.data.participants || []);
      setSelectedEvent(eventId);
      setShowParticipants(true);
    } catch (err) {
      setError('Error al cargar participantes');
      console.error('Error loading participants:', err);
    }
  };

  const canCreateEvents = hasPermission('events', 'create');
  const canManageEvents = hasPermission('events', 'update') || hasPermission('events', 'delete');
  const canParticipate = hasPermission('events', 'participate');

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isEventPast = (eventDate) => {
    return new Date(eventDate) < new Date();
  };

  if (loading) {
    return <div className="loading">Cargando eventos...</div>;
  }

  return (
    <div className="events-container">
      <div className="events-header">
        <h2>Gestión de Eventos</h2>
        {canCreateEvents && (
          <button 
            className="btn btn-primary"
            onClick={() => window.location.href = '/events/new'}
          >
            Crear Evento
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="events-filters">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={includePastEvents}
            onChange={(e) => setIncludePastEvents(e.target.checked)}
          />
          Incluir eventos pasados
        </label>
      </div>

      <div className="events-list">
        {events.length === 0 ? (
          <div className="no-events">No hay eventos disponibles</div>
        ) : (
          events.map(event => (
            <div key={event.id} className={`event-card ${isEventPast(event.eventDate) ? 'past-event' : 'future-event'}`}>
              <div className="event-header">
                <div className="event-title-section">
                  <h3>{event.name}</h3>
                  {userParticipations[event.id] && (
                    <span className="participation-status participating">
                      <span className="status-icon">✓</span>
                      <span className="status-text">Participando</span>
                    </span>
                  )}
                </div>
                <div className="event-date">
                  <span className="date-text">{formatDate(event.eventDate)}</span>
                  {isEventPast(event.eventDate) && (
                    <span className="event-status past">Finalizado</span>
                  )}
                </div>
              </div>
              
              {event.description && (
                <p className="event-description">{event.description}</p>
              )}

              <div className="event-actions">
                {/* Botones principales */}
                <div className="primary-actions">
                  {!isEventPast(event.eventDate) && (
                    <>
                      {!userParticipations[event.id] ? (
                        <button
                          className="btn btn-success btn-modern"
                          onClick={() => handleJoinEvent(event.id)}
                        >
                          ✓ Participar
                        </button>
                      ) : (
                        <button
                          className="btn btn-outline btn-modern"
                          onClick={() => handleLeaveEvent(event.id)}
                        >
                          ✗ Salir del evento
                        </button>
                      )}
                    </>
                  )}
                  
                  <button
                    className="btn btn-secondary btn-modern"
                    onClick={() => loadParticipants(event.id)}
                  >
                    👥 Ver participantes
                  </button>
                </div>

                {/* Botones de gestión (solo para administradores) */}
                {canManageEvents && (
                  <div className="admin-actions">
                    <button
                      className="btn btn-primary btn-small"
                      onClick={() => window.location.href = `/events/${event.id}/edit`}
                    >
                      Editar
                    </button>
                    
                    <button
                      className="btn btn-info btn-small"
                      onClick={() => window.location.href = `/events/${event.id}/participants`}
                    >
                      Gestionar
                    </button>

                    {!isEventPast(event.eventDate) ? (
                      <button
                        className="btn btn-danger btn-small"
                        onClick={() => handleDeleteEvent(event.id)}
                      >
                        Eliminar
                      </button>
                    ) : (
                      <>
                        <button
                          className="btn btn-success btn-small"
                          onClick={() => window.location.href = `/events/${event.id}/donations`}
                        >
                          Registrar Donaciones
                        </button>
                        <button
                          className="btn btn-info btn-small"
                          onClick={() => window.location.href = `/events/${event.id}/donations-history`}
                        >
                          Ver Historial
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal para mostrar participantes */}
      {showParticipants && (
        <div className="modal-overlay" onClick={() => setShowParticipants(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Participantes del Evento</h3>
              <button 
                className="modal-close"
                onClick={() => setShowParticipants(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              {participants.length === 0 ? (
                <p>No hay participantes registrados</p>
              ) : (
                <ul className="participants-list">
                  {participants.map(participant => (
                    <li key={participant.userId}>
                      {participant.userName} {participant.userLastName}
                      <span className="adhesion-date">
                        (Inscrito: {formatDate(participant.adhesionDate)})
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventList;