import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './Inscriptions.css';

const PendingInscriptions = () => {
  const { user } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    if (user && ['PRESIDENTE', 'VOCAL'].includes(user.role)) {
      fetchPendingInscriptions();
    }
  }, [user]);

  const fetchPendingInscriptions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/messaging/pending-inscriptions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const data = await response.json();

      if (data.success) {
        setSolicitudes(data.solicitudes || []);
      } else {
        setError(data.error || 'Error al cargar solicitudes');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessInscription = async (solicitudId, accion, comentarios = '') => {
    try {
      setProcessingId(solicitudId);
      
      const response = await fetch('/api/messaging/process-inscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          solicitud_id: solicitudId,
          accion,
          comentarios
        })
      });

      const data = await response.json();

      if (data.success) {
        // Actualizar la lista
        setSolicitudes(prev => 
          prev.filter(s => s.solicitud_id !== solicitudId)
        );
        
        // Mostrar mensaje de éxito
        alert(`Solicitud ${accion.toLowerCase()}da exitosamente`);
      } else {
        alert(data.error || 'Error al procesar solicitud');
      }
    } catch (err) {
      alert('Error de conexión');
    } finally {
      setProcessingId(null);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-AR');
  };

  if (!user || !['PRESIDENTE', 'VOCAL'].includes(user.role)) {
    return (
      <div className="inscriptions-container">
        <div className="access-denied">
          <h3>Acceso Denegado</h3>
          <p>Solo PRESIDENTE y VOCAL pueden ver solicitudes de inscripción.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="inscriptions-container">
        <div className="loading">Cargando solicitudes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="inscriptions-container">
        <div className="error-message">{error}</div>
        <button onClick={fetchPendingInscriptions} className="retry-button">
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="inscriptions-container">
      <div className="inscriptions-header">
        <h2>Solicitudes de Inscripción Pendientes</h2>
        <button onClick={fetchPendingInscriptions} className="refresh-button">
          🔄 Actualizar
        </button>
      </div>

      {solicitudes.length === 0 ? (
        <div className="no-inscriptions">
          <p>No hay solicitudes de inscripción pendientes.</p>
        </div>
      ) : (
        <div className="inscriptions-list">
          {solicitudes.map((solicitud) => (
            <div key={solicitud.id} className="inscription-card">
              <div className="inscription-header">
                <h3>{solicitud.nombre} {solicitud.apellido}</h3>
                <span className="inscription-role">
                  {solicitud.rol_solicitado}
                </span>
              </div>

              <div className="inscription-details">
                <div className="detail-row">
                  <strong>Email:</strong> {solicitud.email}
                </div>
                {solicitud.telefono && (
                  <div className="detail-row">
                    <strong>Teléfono:</strong> {solicitud.telefono}
                  </div>
                )}
                <div className="detail-row">
                  <strong>Fecha de solicitud:</strong> {formatDate(solicitud.fecha_solicitud)}
                </div>
                {solicitud.mensaje && (
                  <div className="detail-row">
                    <strong>Mensaje:</strong>
                    <p className="inscription-message">{solicitud.mensaje}</p>
                  </div>
                )}
              </div>

              <div className="inscription-actions">
                <button
                  className="approve-button"
                  onClick={() => {
                    const comentarios = prompt('Comentarios (opcional):');
                    if (comentarios !== null) {
                      handleProcessInscription(solicitud.solicitud_id, 'APROBAR', comentarios);
                    }
                  }}
                  disabled={processingId === solicitud.solicitud_id}
                >
                  {processingId === solicitud.solicitud_id ? 'Procesando...' : '✅ Aprobar'}
                </button>
                
                <button
                  className="deny-button"
                  onClick={() => {
                    const comentarios = prompt('Motivo del rechazo (opcional):');
                    if (comentarios !== null) {
                      handleProcessInscription(solicitud.solicitud_id, 'DENEGAR', comentarios);
                    }
                  }}
                  disabled={processingId === solicitud.solicitud_id}
                >
                  {processingId === solicitud.solicitud_id ? 'Procesando...' : '❌ Denegar'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PendingInscriptions;