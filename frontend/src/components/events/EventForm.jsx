import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Events.css';

const EventForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, hasPermission } = useAuth();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    eventDate: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [users, setUsers] = useState([]);
  const [selectedParticipants, setSelectedParticipants] = useState([]);

  useEffect(() => {
    loadUsers();
    if (isEditing) {
      loadEvent();
    }
  }, [id]);

  const loadUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data.users || []);
    } catch (err) {
      console.error('Error loading users:', err);
    }
  };

  const loadEvent = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/events/${id}`);
      const event = response.data.event;
      
      setFormData({
        name: event.name,
        description: event.description || '',
        eventDate: event.eventDate ? new Date(event.eventDate).toISOString().slice(0, 16) : ''
      });

      // Load participants
      const participantsResponse = await api.get(`/events/${id}/participants`);
      const participantIds = participantsResponse.data.participants?.map(p => p.userId) || [];
      setSelectedParticipants(participantIds);
    } catch (err) {
      setError('Error al cargar evento');
      console.error('Error loading event:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleParticipantToggle = (userId) => {
    setSelectedParticipants(prev => {
      if (prev.includes(userId)) {
        return prev.filter(id => id !== userId);
      } else {
        return [...prev, userId];
      }
    });
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError('El nombre del evento es requerido');
      return false;
    }

    if (!formData.eventDate) {
      setError('La fecha del evento es requerida');
      return false;
    }

    const eventDate = new Date(formData.eventDate);
    if (eventDate <= new Date()) {
      setError('La fecha del evento debe ser futura');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError('');

      const eventData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        eventDate: formData.eventDate,
        participantIds: selectedParticipants
      };

      if (isEditing) {
        await api.put(`/events/${id}`, eventData);
        
        // Update participants separately for editing
        const currentParticipants = await api.get(`/events/${id}/participants`);
        const currentParticipantIds = currentParticipants.data.participants?.map(p => p.userId) || [];
        
        // Add new participants
        for (const userId of selectedParticipants) {
          if (!currentParticipantIds.includes(userId)) {
            try {
              await api.post(`/events/${id}/participants`, { userId });
            } catch (err) {
              console.error('Error adding participant:', err);
            }
          }
        }
        
        // Remove participants
        for (const userId of currentParticipantIds) {
          if (!selectedParticipants.includes(userId)) {
            try {
              await api.delete(`/events/${id}/participants/${userId}`);
            } catch (err) {
              console.error('Error removing participant:', err);
            }
          }
        }
      } else {
        await api.post('/events', eventData);
      }

      navigate('/events');
    } catch (err) {
      setError(err.response?.data?.error || 'Error al guardar evento');
      console.error('Error saving event:', err);
    } finally {
      setLoading(false);
    }
  };

  const canManageEvents = hasPermission('events', 'create') || hasPermission('events', 'update');

  if (!canManageEvents) {
    return (
      <div className="error-message">
        No tiene permisos para crear o editar eventos
      </div>
    );
  }

  if (loading && isEditing) {
    return <div className="loading">Cargando evento...</div>;
  }

  return (
    <div className="event-form-container">
      <div className="form-header">
        <h2>{isEditing ? 'Editar Evento' : 'Crear Nuevo Evento'}</h2>
        <button 
          className="btn btn-secondary"
          onClick={() => navigate('/events')}
        >
          Volver
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="event-form">
        <div className="form-group">
          <label htmlFor="name">Nombre del Evento *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            maxLength={255}
            placeholder="Ingrese el nombre del evento"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Descripción</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={4}
            placeholder="Ingrese una descripción del evento"
          />
        </div>

        <div className="form-group">
          <label htmlFor="eventDate">Fecha y Hora del Evento *</label>
          <input
            type="datetime-local"
            id="eventDate"
            name="eventDate"
            value={formData.eventDate}
            onChange={handleInputChange}
            required
            min={new Date().toISOString().slice(0, 16)}
          />
        </div>

        <div className="form-group">
          <label>Participantes</label>
          <div className="participants-selection">
            {users.filter(u => u.active).map(user => (
              <label key={user.id} className="participant-checkbox">
                <input
                  type="checkbox"
                  checked={selectedParticipants.includes(user.id)}
                  onChange={() => handleParticipantToggle(user.id)}
                />
                {user.firstName} {user.lastName} ({user.role})
              </label>
            ))}
          </div>
        </div>

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
            disabled={loading}
          >
            {loading ? 'Guardando...' : (isEditing ? 'Actualizar' : 'Crear')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EventForm;