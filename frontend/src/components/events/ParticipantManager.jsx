import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Events.css';

const ParticipantManager = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, hasPermission } = useAuth();

  const [event, setEvent] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedUserId, setSelectedUserId] = useState('');

  useEffect(() => {
    loadEventData();
  }, [id]);

  const loadEventData = async () => {
    try {
      setLoading(true);

      // Load event details
      const eventResponse = await api.get(`/events/${id}`);
      setEvent(eventResponse.data.event);

      // Load participants
      const participantsResponse = await api.get(`/events/${id}/participants`);
      setParticipants(participantsResponse.data.participants || []);

      // Load all active users
      const usersResponse = await api.get('/users');
      const allUsers = usersResponse.data.users || [];

      // Filter out users who are already participants
      const participantIds = participantsResponse.data.participants?.map(p => p.userId) || [];
      const available = allUsers.filter(u => u.isActive && !participantIds.includes(u.id));
      setAvailableUsers(available);

      setError('');
    } catch (err) {
      setError('Error al cargar datos del evento');
      console.error('Error loading event data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddParticipant = async () => {
    if (!selectedUserId) {
      setError('Seleccione un usuario para agregar');
      return;
    }

    try {
      await api.post(`/events/${id}/participants`, {
        userId: parseInt(selectedUserId)
      });

      setSelectedUserId('');
      loadEventData(); // Reload to update lists
    } catch (err) {
      setError('Error al agregar participante');
      console.error('Error adding participant:', err);
    }
  };

  const handleRemoveParticipant = async (userId) => {
    if (!window.confirm('¿Está seguro de que desea quitar este participante?')) {
      return;
    }

    try {
      await api.delete(`/events/${id}/participants/${userId}`);
      loadEventData(); // Reload to update lists
    } catch (err) {
      setError('Error al quitar participante');
      console.error('Error removing participant:', err);
    }
  };

  const canManageParticipants = hasPermission('events', 'update');

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="loading">Cargando datos del evento...</div>;
  }

  if (!event) {
    return <div className="error-message">Evento no encontrado</div>;
  }

  return (
    <div className="participant-manager-container">
      <div className="form-header">
        <h2>Gestión de Participantes</h2>
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

      {canManageParticipants && (
        <div className="add-participant-section">
          <h4>Agregar Participante</h4>
          <div className="add-participant-form">
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              className="user-select"
            >
              <option value="">Seleccionar usuario...</option>
              {availableUsers.map(user => (
                <option key={user.id} value={user.id}>
                  {user.firstName} {user.lastName} ({user.role})
                </option>
              ))}
            </select>
            <button
              className="btn btn-primary"
              onClick={handleAddParticipant}
              disabled={!selectedUserId}
            >
              Agregar
            </button>
          </div>
        </div>
      )}

      <div className="participants-section">
        <h4>Participantes Actuales ({participants.length})</h4>
        {participants.length === 0 ? (
          <div className="no-participants">No hay participantes registrados</div>
        ) : (
          <div className="participants-list">
            {participants.map(participant => (
              <div key={participant.userId} className="participant-item">
                <div className="participant-info">
                  <span className="participant-name">
                    {participant.userName} {participant.userLastName}
                  </span>
                  <span className="adhesion-date">
                    Inscrito: {formatDate(participant.adhesionDate)}
                  </span>
                </div>
                {canManageParticipants && (
                  <button
                    className="btn btn-danger btn-small"
                    onClick={() => handleRemoveParticipant(participant.userId)}
                  >
                    Quitar
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {availableUsers.length === 0 && canManageParticipants && (
        <div className="info-message">
          Todos los usuarios activos ya están participando en este evento
        </div>
      )}
    </div>
  );
};

export default ParticipantManager;