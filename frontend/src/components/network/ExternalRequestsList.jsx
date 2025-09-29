import React, { useState, useEffect } from 'react';
import { messagingService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import DonationTransferForm from './DonationTransferForm';

const ExternalRequestsList = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showTransferForm, setShowTransferForm] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const { user } = useAuth();

  const categories = [
    { value: '', label: 'Todas las categorías' },
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  const fetchExternalRequests = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {};
      if (selectedCategory) {
        params.category = selectedCategory;
      }

      const response = await messagingService.getExternalRequests(params);
      
      if (response.data.success) {
        setRequests(response.data.requests || []);
      } else {
        setError(response.data.error || 'Error al cargar solicitudes externas');
      }
    } catch (err) {
      console.error('Error al cargar solicitudes externas:', err);
      setError(err.response?.data?.error || 'Error al cargar solicitudes externas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExternalRequests();
  }, [selectedCategory]);

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

  const handleTransferDonations = (request) => {
    setSelectedRequest(request);
    setShowTransferForm(true);
  };

  const handleTransferSuccess = () => {
    setShowTransferForm(false);
    setSelectedRequest(null);
    // Recargar las solicitudes para reflejar cambios
    fetchExternalRequests();
  };

  const handleTransferCancel = () => {
    setShowTransferForm(false);
    setSelectedRequest(null);
  };

  if (loading) {
    return (
      <div className="external-requests-container">
        <div className="loading">Cargando solicitudes externas...</div>
      </div>
    );
  }

  if (showTransferForm && selectedRequest) {
    return (
      <div className="transfer-form-container">
        <DonationTransferForm
          targetRequest={selectedRequest}
          onSuccess={handleTransferSuccess}
          onCancel={handleTransferCancel}
        />
      </div>
    );
  }

  return (
    <div className="external-requests-container">
      <div className="section-header">
        <h3>Solicitudes de Donaciones de Otras ONGs</h3>
        <p>Aquí puede ver las solicitudes de donaciones de otras organizaciones de la red.</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Filtros */}
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="category-filter">Filtrar por categoría:</label>
          <select
            id="category-filter"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(category => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
        </div>
        <button 
          className="btn btn-secondary"
          onClick={fetchExternalRequests}
        >
          Actualizar
        </button>
      </div>

      {/* Lista de solicitudes */}
      <div className="requests-list">
        {requests.length === 0 ? (
          <div className="no-requests">
            No hay solicitudes externas disponibles
            {selectedCategory && ` en la categoría ${getCategoryLabel(selectedCategory)}`}
          </div>
        ) : (
          <div className="requests-grid">
            {requests.map(request => (
              <div key={`${request.organization_id}-${request.request_id}`} className="request-card">
                <div className="request-header">
                  <h4>Solicitud de {request.organization_id}</h4>
                  <span className="request-date">
                    {formatDate(request.timestamp)}
                  </span>
                </div>
                
                <div className="request-content">
                  <div className="request-info">
                    <strong>ID de Solicitud:</strong> {request.request_id}
                  </div>
                  
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

                <div className="request-actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => handleTransferDonations(request)}
                  >
                    Transferir Donaciones
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
          <li>Las solicitudes se actualizan automáticamente cuando otras ONGs publican nuevas necesidades</li>
          <li>Puede filtrar por categoría para encontrar solicitudes específicas</li>
          <li>Use "Transferir Donaciones" para enviar ayuda a otras organizaciones</li>
          <li>Solo se muestran solicitudes activas de otras organizaciones</li>
        </ul>
      </div>
    </div>
  );
};

export default ExternalRequestsList;