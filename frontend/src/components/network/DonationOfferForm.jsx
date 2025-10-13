import React, { useState, useEffect } from 'react';
import { messagingService, inventoryService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const DonationOfferForm = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    offers: []
  });
  const [availableInventory, setAvailableInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingInventory, setLoadingInventory] = useState(true);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const { user } = useAuth();

  const categories = [
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  useEffect(() => {
    fetchAvailableInventory();
  }, []);

  const fetchAvailableInventory = async () => {
    try {
      setLoadingInventory(true);
      const response = await inventoryService.getDonations();
      
      if (response.data.success) {
        // Filtrar solo donaciones activas (no eliminadas) con cantidad > 0
        const activeInventory = (response.data.donations || []).filter(
          donation => !donation.deleted && donation.quantity > 0
        );
        setAvailableInventory(activeInventory);
        
        // Inicializar con una oferta vacía
        if (activeInventory.length > 0) {
          setFormData({
            offers: [{ selectedInventoryId: '', quantity: '', description: '' }]
          });
        }
      } else {
        setError('Error al cargar inventario disponible');
      }
    } catch (err) {
      console.error('Error al cargar inventario:', err);
      setError('Error al cargar inventario disponible');
    } finally {
      setLoadingInventory(false);
    }
  };

  const validateForm = () => {
    const errors = {};

    // Validar que hay al menos una oferta
    if (!formData.offers || formData.offers.length === 0) {
      errors.offers = 'Debe agregar al menos una donación para ofrecer';
      setValidationErrors(errors);
      return false;
    }

    // Validar que hay al menos una oferta válida
    const validOffers = formData.offers.filter(offer => 
      offer.selectedInventoryId && offer.quantity && parseInt(offer.quantity) > 0
    );

    if (validOffers.length === 0) {
      errors.offers = 'Debe especificar al menos una donación válida para ofrecer';
      setValidationErrors(errors);
      return false;
    }

    // Validar cada oferta
    const offerErrors = [];
    formData.offers.forEach((offer, index) => {
      const offerError = {};
      
      if (!offer.selectedInventoryId) {
        offerError.selectedInventoryId = 'Debe seleccionar una donación del inventario';
      }
      
      if (!offer.quantity) {
        offerError.quantity = 'La cantidad es obligatoria';
      } else {
        const quantity = parseInt(offer.quantity);
        const selectedItem = availableInventory.find(item => item.id.toString() === offer.selectedInventoryId);
        
        if (isNaN(quantity) || quantity <= 0) {
          offerError.quantity = 'La cantidad debe ser un número positivo';
        } else if (selectedItem && quantity > selectedItem.quantity) {
          offerError.quantity = `Cantidad máxima disponible: ${selectedItem.quantity}`;
        }
      }
      
      if (Object.keys(offerError).length > 0) {
        offerErrors[index] = offerError;
      }
    });

    if (offerErrors.length > 0) {
      errors.offers = offerErrors;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleOfferChange = (index, field, value) => {
    const newOffers = [...formData.offers];
    newOffers[index] = {
      ...newOffers[index],
      [field]: value
    };

    // Si se selecciona un item del inventario, actualizar la descripción automáticamente
    if (field === 'selectedInventoryId' && value) {
      const selectedItem = availableInventory.find(item => item.id.toString() === value);
      if (selectedItem) {
        newOffers[index].description = selectedItem.name || selectedItem.description || selectedItem.category;
        newOffers[index].category = selectedItem.category;
      }
    }
    
    setFormData(prev => ({
      ...prev,
      offers: newOffers
    }));

    // Limpiar errores de validación
    if (validationErrors.offers && validationErrors.offers[index]) {
      const newErrors = { ...validationErrors };
      if (newErrors.offers[index]) {
        delete newErrors.offers[index][field];
        if (Object.keys(newErrors.offers[index]).length === 0) {
          delete newErrors.offers[index];
        }
      }
      setValidationErrors(newErrors);
    }
  };

  const addOffer = () => {
    setFormData(prev => ({
      ...prev,
      offers: [...prev.offers, { selectedInventoryId: '', quantity: '', description: '' }]
    }));
  };

  const removeOffer = (index) => {
    if (formData.offers.length > 1) {
      const newOffers = formData.offers.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        offers: newOffers
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Preparar datos de oferta solo para items válidos
      const validOffers = formData.offers.filter(offer => 
        offer.selectedInventoryId && offer.quantity && parseInt(offer.quantity) > 0
      );

      const offerData = {
        donations: validOffers.map(offer => {
          const selectedItem = availableInventory.find(item => item.id.toString() === offer.selectedInventoryId);
          return {
            category: selectedItem.category,
            description: offer.description || selectedItem.name || selectedItem.description || selectedItem.category,
            quantity: `${offer.quantity}${selectedItem?.unit || ''}`,
            inventoryId: parseInt(offer.selectedInventoryId)
          };
        })
      };

      const response = await messagingService.createDonationOffer(offerData);

      if (response.data.success) {
        onSuccess && onSuccess();
      } else {
        setError(response.data.error || 'Error al crear oferta de donación');
      }
    } catch (err) {
      console.error('Error al crear oferta:', err);
      setError(err.response?.data?.error || 'Error al crear oferta de donación');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLabel = (categoryValue) => {
    const category = categories.find(c => c.value === categoryValue);
    return category ? category.label : categoryValue;
  };

  if (loadingInventory) {
    return (
      <div className="offer-form-container">
        <div className="loading">Cargando inventario disponible...</div>
      </div>
    );
  }

  if (availableInventory.length === 0) {
    return (
      <div className="offer-form-container">
        <div className="no-inventory">
          <h3>No hay donaciones disponibles para ofrecer</h3>
          <p>Debe tener donaciones en su inventario para poder crear ofertas.</p>
          <button className="btn btn-secondary" onClick={onCancel}>
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="donation-offer-form">
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-section">
          <h4>Donaciones a Ofrecer</h4>
          <p className="form-help">
            Seleccione las donaciones de su inventario que desea ofrecer a la red de ONGs.
            Las ofertas serán visibles para todas las organizaciones de la red.
          </p>

          {formData.offers.map((offer, index) => {
            const selectedItem = availableInventory.find(item => item.id.toString() === offer.selectedInventoryId);
            
            return (
              <div key={index} className="offer-item">
                <div className="offer-header">
                  <h5>Oferta {index + 1}</h5>
                  {formData.offers.length > 1 && (
                    <button
                      type="button"
                      className="btn btn-sm btn-danger"
                      onClick={() => removeOffer(index)}
                      disabled={loading}
                    >
                      Eliminar
                    </button>
                  )}
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor={`inventory-${index}`}>
                      Seleccionar donación del inventario <span className="required">*</span>
                    </label>
                    <select
                      id={`inventory-${index}`}
                      value={offer.selectedInventoryId}
                      onChange={(e) => handleOfferChange(index, 'selectedInventoryId', e.target.value)}
                      className={validationErrors.offers?.[index]?.selectedInventoryId ? 'error' : ''}
                      disabled={loading}
                    >
                      <option value="">Seleccionar donación</option>
                      {availableInventory.map(item => (
                        <option key={item.id} value={item.id}>
                          {getCategoryLabel(item.category)} - {item.name || item.description || item.category} (Disponible: {item.quantity})
                        </option>
                      ))}
                    </select>
                    {validationErrors.offers?.[index]?.selectedInventoryId && (
                      <div className="field-error">
                        {validationErrors.offers[index].selectedInventoryId}
                      </div>
                    )}
                  </div>

                  <div className="form-group">
                    <label htmlFor={`quantity-${index}`}>
                      Cantidad a ofrecer <span className="required">*</span>
                    </label>
                    <input
                      type="number"
                      id={`quantity-${index}`}
                      value={offer.quantity}
                      onChange={(e) => handleOfferChange(index, 'quantity', e.target.value)}
                      placeholder="Cantidad"
                      min="1"
                      max={selectedItem?.quantity || undefined}
                      className={validationErrors.offers?.[index]?.quantity ? 'error' : ''}
                      disabled={loading || !offer.selectedInventoryId}
                    />
                    {validationErrors.offers?.[index]?.quantity && (
                      <div className="field-error">
                        {validationErrors.offers[index].quantity}
                      </div>
                    )}
                    {selectedItem && (
                      <div className="field-info">
                        Máximo disponible: {selectedItem.quantity}
                      </div>
                    )}
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor={`description-${index}`}>
                    Descripción personalizada
                  </label>
                  <textarea
                    id={`description-${index}`}
                    value={offer.description}
                    onChange={(e) => handleOfferChange(index, 'description', e.target.value)}
                    placeholder="Descripción adicional para la oferta (opcional)"
                    rows="2"
                    disabled={loading}
                  />
                  <div className="field-info">
                    Si no especifica una descripción, se usará la descripción del inventario
                  </div>
                </div>
              </div>
            );
          })}

          <button
            type="button"
            className="btn btn-secondary"
            onClick={addOffer}
            disabled={loading}
          >
            + Agregar otra donación
          </button>
        </div>

        {/* Botones */}
        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Publicando...' : 'Publicar Oferta'}
          </button>
        </div>
      </form>

      <div className="form-info">
        <h4>Información importante:</h4>
        <ul>
          <li>Las ofertas se publican a toda la red de ONGs</li>
          <li>Solo puede ofrecer donaciones que tiene disponibles en su inventario</li>
          <li>Las cantidades ofrecidas no se reservan hasta que otra organización las solicite</li>
          <li>Puede crear múltiples ofertas con diferentes donaciones</li>
          <li>Las ofertas permanecen activas hasta que las retire manualmente</li>
        </ul>
      </div>
    </div>
  );
};

export default DonationOfferForm;