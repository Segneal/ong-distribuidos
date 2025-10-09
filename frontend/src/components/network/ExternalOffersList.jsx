import React, { useState, useEffect } from 'react';
import { messagingService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const ExternalOffersList = () => {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const { user } = useAuth();

  const categories = [
    { value: '', label: 'Todas las categorías' },
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  const fetchExternalOffers = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {};
      if (selectedCategory) {
        params.category = selectedCategory;
      }
      if (searchTerm.trim()) {
        params.search = searchTerm.trim();
      }

      const response = await messagingService.getExternalOffers(params);
      
      if (response.data.success) {
        setOffers(response.data.offers || []);
      } else {
        setError(response.data.error || 'Error al cargar ofertas externas');
      }
    } catch (err) {
      console.error('Error al cargar ofertas externas:', err);
      setError(err.response?.data?.error || 'Error al cargar ofertas externas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExternalOffers();
  }, [selectedCategory]);

  const handleSearch = () => {
    fetchExternalOffers();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

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

  const handleContactOrganization = (offer) => {
    // Esta funcionalidad podría expandirse para incluir un sistema de mensajería
    alert(`Para contactar a ${offer.donor_organization}, use los canales oficiales de la red de ONGs.`);
  };

  if (loading) {
    return (
      <div className="external-offers-container">
        <div className="loading">Cargando ofertas externas...</div>
      </div>
    );
  }

  return (
    <div className="external-offers-container">
      <div className="section-header">
        <h3>Ofertas de Donaciones Disponibles</h3>
        <p>Explore las donaciones que otras organizaciones de la red tienen disponibles para ofrecer.</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Filtros y búsqueda */}
      <div className="filters">
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

        <div className="filter-group search-group">
          <label htmlFor="search-input">Buscar:</label>
          <input
            type="text"
            id="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Buscar en descripciones..."
          />
          <button 
            className="btn btn-secondary"
            onClick={handleSearch}
          >
            Buscar
          </button>
        </div>

        <button 
          className="btn btn-secondary"
          onClick={fetchExternalOffers}
        >
          Actualizar
        </button>
      </div>

      {/* Lista de ofertas */}
      <div className="offers-list">
        {offers.length === 0 ? (
          <div className="no-offers">
            No hay ofertas externas disponibles
            {selectedCategory && ` en la categoría ${getCategoryLabel(selectedCategory)}`}
            {searchTerm && ` que coincidan con "${searchTerm}"`}
          </div>
        ) : (
          <div className="offers-grid">
            {offers.map(offer => (
              <div key={`${offer.donor_organization}-${offer.offer_id}`} className="offer-card">
                <div className="offer-header">
                  <h4>Oferta de {offer.donor_organization}</h4>
                  <span className="offer-date">
                    {formatDate(offer.timestamp)}
                  </span>
                </div>
                
                <div className="offer-content">
                  <div className="offer-info">
                    <strong>ID de Oferta:</strong> {offer.offer_id}
                  </div>
                  
                  <div className="donations-offered">
                    <h5>Donaciones Disponibles:</h5>
                    <div className="donations-list">
                      {offer.donations.map((donation, index) => (
                        <div key={index} className="donation-item">
                          <div className="donation-category">
                            <span className="category-badge">
                              {getCategoryLabel(donation.category)}
                            </span>
                          </div>
                          <div className="donation-details">
                            <div className="donation-description">
                              <strong>{donation.description}</strong>
                            </div>
                            <div className="donation-quantity">
                              <span className="quantity-badge">
                                📦 {donation.cantidad || donation.quantity} disponible
                              </span>
                            </div>
                            <div className="donation-status">
                              <span className="status-available">✅ Disponible</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="offer-actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => handleContactOrganization(offer)}
                  >
                    Contactar Organización
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
          <li>Las ofertas se actualizan automáticamente cuando otras ONGs publican nuevas donaciones</li>
          <li>Puede filtrar por categoría y buscar en las descripciones</li>
          <li>Use "Contactar Organización" para coordinar la obtención de donaciones</li>
          <li>Solo se muestran ofertas activas de otras organizaciones</li>
          <li>Las cantidades mostradas pueden cambiar si otras organizaciones ya han solicitado parte de las donaciones</li>
        </ul>
      </div>
    </div>
  );
};

export default ExternalOffersList;