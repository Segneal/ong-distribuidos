import React, { useState, useEffect } from 'react';
import { messagingService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const ActiveRequestsList = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancellingRequest, setCancellingRequest] = useState(null);
  const { user } = useAuth();

  const categories = [
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  const fetchActiveRequests = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await messagingService.getActiveRequests();
      
      if (response.data.success) {
        setRequests(response.data.requests || []);
      } else {
        setError(response.data.error || 'Error al cargar solicitudes activas');
      }
    } catch (err) {
      console.error('Error al cargar solicitudes activas:', err);
      setError(err.response?.data?.error || 'Error al cargar solicitudes activas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveRequests();
  }, []);

  const getCategoryLabel = (category) => {
    const cat = categories.find(c => c.value === category);
    return cat ? cat.label : category;
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

  const handleCancelRequest = async (requestId) => {
    if (!window.confirm('¿Está seguro que desea dar de baja esta solicitud? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      setCancellingRequest(requestId);
      setError('');
      
      const response = await messagingService.cancelDonationRequest(requestId);
      
      if (response.data.success) {
        // Recargar la lista para reflejar los cambios
        await fetchActiveRequests();
      } else {
        setError(response.data.error || 'Error al dar de baja la solicitud');
      }
    } catch (err) {
      console.error('Error al dar de baja solicitud:', err);
      setError(err.response?.data?.error || 'Error al dar de baja la solicitud');
    } finally {
      setCancellingRequest(null);
    }
  };

  if (loading) {
    return (
      <div className="active-requests-container">
        <div className="loading">Cargando solicitudes activas...</div>
      </div>
    );
  }

  return (
    <div className="active-requests-container">
      <div className="section-header">
        <h3>Mis Solicitudes Activas</h3>
        <p>Solicitudes de donaciones que su organización ha enviado a la red.</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="section-actions">
        <button 
          className="btn btn-secondary"
          onClick={fetchActiveRequests}
          disabled={loading}
        >
          Actualizar
        </button>
      </div>

      {/* Lista de solicitudes */}
      <div className="requests-list">
        {requests.length === 0 ? (
          <div className="no-requests">
            No tiene solicitudes activas en este momento.
            <br />
            <small>Las solicitudes aparecerán aquí después de crearlas.</small>
          </div>
        ) : (
          <div className="requests-grid">
            {requests.map(request => (
              <div key={request.request_id} className="request-card own-request">
                <div className="request-header">
                  <h4>Solicitud #{request.request_id}</h4>
                  <span className="request-date">
                    Creada: {formatDate(request.timestamp)}
                  </span>
                </div>
                
                <div className="request-content">
                  <div className="donations-requested">
                    <h5>Donaciones Solicitadas:</h5>
                    <div className="donations-list">
                      {request.donations.map((donation, index) => (
                        <div key={index} className="donation-item">
                          <div className="donation-category">
                            <span className="category-badge">
                              {getCategoryLabel(donation.category)}
                            </span>
                          </div>
                          <div className="donation-description">
                            {donation.description}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="request-status">
                  <span className="status-badge active">
                    Activa
                  </span>
                </div>

                <div className="request-actions">
                  <button
                    className="btn btn-danger"
                    onClick={() => handleCancelRequest(request.request_id)}
                    disabled={cancellingRequest === request.request_id}
                  >
                    {cancellingRequest === request.request_id ? 'Dando de baja...' : 'Dar de Baja'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="section-info">
        <h4>Información:</h4>
        <ul>
          <li>Las solicitudes activas son visibles para todas las ONGs de la red</li>
          <li>Puede dar de baja una solicitud cuando ya no la necesite</li>
          <li>Las solicitudes dadas de baja no aparecerán más en la red</li>
          <li>Recibirá transferencias de donaciones en respuesta a estas solicitudes</li>
        </ul>
      </div>
    </div>
  );
};

export default ActiveRequestsList;