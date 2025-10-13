import React, { useState, useEffect } from 'react';
import { messagingService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const TransferHistory = () => {
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('');
  const { user } = useAuth();

  const categories = [
    { value: '', label: 'Todas las categorías' },
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  const transferTypes = [
    { value: 'all', label: 'Todas las transferencias' },
    { value: 'sent', label: 'Enviadas' },
    { value: 'received', label: 'Recibidas' }
  ];

  const fetchTransferHistory = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {};
      if (filterType !== 'all') {
        params.type = filterType === 'sent' ? 'ENVIADA' : 'RECIBIDA';
      }
      if (selectedCategory) {
        params.category = selectedCategory;
      }

      const response = await messagingService.getTransferHistory(params);
      
      if (response.data && response.data.success) {
        const transfersData = response.data.transfers || [];
        // Asegurar que cada transfer tenga la estructura correcta
        const validTransfers = transfersData.map(transfer => ({
          ...transfer,
          donations: transfer.donations || transfer.donaciones || [],
          donaciones: transfer.donations || transfer.donaciones || []
        }));
        setTransfers(validTransfers);
      } else {
        setError(response.data?.error || 'Error al cargar historial de transferencias');
        setTransfers([]);
      }
    } catch (err) {
      console.error('Error al cargar historial:', err);
      setError(err.response?.data?.error || 'Error al cargar historial de transferencias');
      setTransfers([]); // Asegurar que transfers sea un array vacío en caso de error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransferHistory();
  }, [filterType, selectedCategory]);

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

  const getTransferTypeLabel = (type) => {
    return type === 'ENVIADA' ? 'Enviada' : 'Recibida';
  };

  const getTransferTypeClass = (type) => {
    return type === 'ENVIADA' ? 'sent' : 'received';
  };

  if (loading) {
    return (
      <div className="transfer-history-container">
        <div className="loading">Cargando historial de transferencias...</div>
      </div>
    );
  }

  return (
    <div className="transfer-history-container">
      <div className="section-header">
        <h3>Historial de Transferencias</h3>
        <p>Registro de todas las transferencias de donaciones enviadas y recibidas.</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Filtros */}
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="type-filter">Tipo:</label>
          <select
            id="type-filter"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            {transferTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="category-filter">Categoría:</label>
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
          onClick={fetchTransferHistory}
        >
          Actualizar
        </button>
      </div>

      {/* Lista de transferencias */}
      <div className="transfers-list">
        {!Array.isArray(transfers) || transfers.length === 0 ? (
          <div className="no-transfers">
            No hay transferencias en el historial
            {filterType !== 'all' && ` del tipo ${transferTypes.find(t => t.value === filterType)?.label.toLowerCase()}`}
            {selectedCategory && ` en la categoría ${getCategoryLabel(selectedCategory)}`}
          </div>
        ) : (
          <div className="transfers-grid">
            {Array.isArray(transfers) && transfers.map((transfer, index) => (
              <div key={index} className={`transfer-card ${getTransferTypeClass(transfer.tipo)}`}>
                <div className="transfer-header">
                  <div className="transfer-type">
                    <span className={`type-badge ${getTransferTypeClass(transfer.tipo)}`}>
                      {getTransferTypeLabel(transfer.tipo)}
                    </span>
                  </div>
                  <span className="transfer-date">
                    {formatDate(transfer.fecha_transferencia)}
                  </span>
                </div>
                
                <div className="transfer-content">
                  <div className="transfer-info">
                    <div className="info-row">
                      <strong>
                        {transfer.tipo === 'ENVIADA' ? 'Enviado a:' : 'Recibido de:'}
                      </strong> 
                      {transfer.organizacion_contraparte}
                    </div>
                    {transfer.solicitud_id && (
                      <div className="info-row">
                        <strong>Solicitud ID:</strong> {transfer.solicitud_id}
                      </div>
                    )}
                  </div>
                  
                  <div className="donations-transferred">
                    <h5>Donaciones:</h5>
                    <div className="donations-list">
                      {(transfer.donations || transfer.donaciones || []).map((donation, donationIndex) => (
                        <div key={donationIndex} className="donation-item">
                          <div className="donation-category">
                            <span className="category-badge">
                              {getCategoryLabel(donation.category || donation.categoria)}
                            </span>
                          </div>
                          <div className="donation-details">
                            <div className="donation-description">
                              {donation.description || donation.descripcion || 'Donación'}
                            </div>
                            <div className="donation-quantity">
                              <strong>Cantidad:</strong> {donation.quantity || donation.cantidad || '1'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="section-info">
        <h4>Información:</h4>
        <ul>
          <li><strong>Enviadas:</strong> Donaciones que su organización ha transferido a otras ONGs</li>
          <li><strong>Recibidas:</strong> Donaciones que su organización ha recibido de otras ONGs</li>
          <li>Las transferencias enviadas reducen su inventario automáticamente</li>
          <li>Las transferencias recibidas aumentan su inventario automáticamente</li>
          <li>Puede filtrar por tipo de transferencia y categoría de donación</li>
        </ul>
      </div>
    </div>
  );
};

export default TransferHistory;