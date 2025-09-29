import React, { useState, useEffect } from 'react';
import { messagingService, inventoryService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const DonationTransferForm = ({ targetRequest, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    transfers: []
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
    initializeTransfers();
  }, [targetRequest]);

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

  const initializeTransfers = () => {
    if (!targetRequest || !targetRequest.donations) return;

    // Inicializar transferencias basadas en las donaciones solicitadas
    const initialTransfers = targetRequest.donations.map(requestedDonation => ({
      category: requestedDonation.category,
      description: requestedDonation.description,
      requestedDescription: requestedDonation.description,
      quantity: '',
      selectedInventoryId: ''
    }));

    setFormData({ transfers: initialTransfers });
  };

  const validateForm = () => {
    const errors = {};

    // Validar que hay al menos una transferencia con cantidad > 0
    const validTransfers = formData.transfers.filter(t => 
      t.selectedInventoryId && t.quantity && parseInt(t.quantity) > 0
    );

    if (validTransfers.length === 0) {
      errors.transfers = 'Debe especificar al menos una donación para transferir';
      setValidationErrors(errors);
      return false;
    }

    // Validar cada transferencia
    const transferErrors = [];
    formData.transfers.forEach((transfer, index) => {
      if (!transfer.selectedInventoryId && transfer.quantity) {
        const transferError = { selectedInventoryId: 'Debe seleccionar una donación del inventario' };
        transferErrors[index] = transferError;
      }

      if (transfer.selectedInventoryId && transfer.quantity) {
        const selectedItem = availableInventory.find(item => item.id.toString() === transfer.selectedInventoryId);
        const quantity = parseInt(transfer.quantity);

        if (isNaN(quantity) || quantity <= 0) {
          if (!transferErrors[index]) transferErrors[index] = {};
          transferErrors[index].quantity = 'La cantidad debe ser un número positivo';
        } else if (selectedItem && quantity > selectedItem.quantity) {
          if (!transferErrors[index]) transferErrors[index] = {};
          transferErrors[index].quantity = `Cantidad máxima disponible: ${selectedItem.quantity}`;
        }
      }
    });

    if (transferErrors.length > 0) {
      errors.transfers = transferErrors;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleTransferChange = (index, field, value) => {
    const newTransfers = [...formData.transfers];
    newTransfers[index] = {
      ...newTransfers[index],
      [field]: value
    };

    // Si se selecciona un item del inventario, actualizar la descripción
    if (field === 'selectedInventoryId' && value) {
      const selectedItem = availableInventory.find(item => item.id.toString() === value);
      if (selectedItem) {
        newTransfers[index].description = selectedItem.description || selectedItem.category;
      }
    }
    
    setFormData(prev => ({
      ...prev,
      transfers: newTransfers
    }));

    // Limpiar errores de validación
    if (validationErrors.transfers && validationErrors.transfers[index]) {
      const newErrors = { ...validationErrors };
      if (newErrors.transfers[index]) {
        delete newErrors.transfers[index][field];
        if (Object.keys(newErrors.transfers[index]).length === 0) {
          delete newErrors.transfers[index];
        }
      }
      setValidationErrors(newErrors);
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
      // Preparar datos de transferencia solo para items con cantidad > 0
      const validTransfers = formData.transfers.filter(t => 
        t.selectedInventoryId && t.quantity && parseInt(t.quantity) > 0
      );

      const transferData = {
        targetOrganization: targetRequest.organization_id,
        requestId: targetRequest.request_id,
        donations: validTransfers.map(transfer => {
          const selectedItem = availableInventory.find(item => item.id.toString() === transfer.selectedInventoryId);
          return {
            category: transfer.category,
            description: transfer.description,
            quantity: `${transfer.quantity}${selectedItem?.unit || ''}`,
            inventoryId: parseInt(transfer.selectedInventoryId)
          };
        })
      };

      const response = await messagingService.transferDonations(transferData);

      if (response.data.success) {
        onSuccess && onSuccess();
      } else {
        setError(response.data.error || 'Error al transferir donaciones');
      }
    } catch (err) {
      console.error('Error al transferir donaciones:', err);
      setError(err.response?.data?.error || 'Error al transferir donaciones');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLabel = (categoryValue) => {
    const category = categories.find(c => c.value === categoryValue);
    return category ? category.label : categoryValue;
  };

  const getInventoryByCategory = (category) => {
    return availableInventory.filter(item => item.category === category);
  };

  if (loadingInventory) {
    return (
      <div className="transfer-form-container">
        <div className="loading">Cargando inventario disponible...</div>
      </div>
    );
  }

  return (
    <div className="donation-transfer-form">
      <div className="transfer-header">
        <h3>Transferir Donaciones</h3>
        <div className="target-info">
          <strong>Organización destino:</strong> {targetRequest.organization_id}
          <br />
          <strong>Solicitud ID:</strong> {targetRequest.request_id}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-section">
          <h4>Donaciones Solicitadas</h4>
          <p className="form-help">
            Seleccione las donaciones de su inventario que desea transferir para cada solicitud.
            Solo se transferirán las donaciones con cantidad especificada.
          </p>

          {formData.transfers.map((transfer, index) => {
            const categoryInventory = getInventoryByCategory(transfer.category);
            
            return (
              <div key={index} className="transfer-item">
                <div className="transfer-header-item">
                  <h5>
                    {getCategoryLabel(transfer.category)} - {transfer.requestedDescription}
                  </h5>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor={`inventory-${index}`}>
                      Seleccionar donación del inventario
                    </label>
                    <select
                      id={`inventory-${index}`}
                      value={transfer.selectedInventoryId}
                      onChange={(e) => handleTransferChange(index, 'selectedInventoryId', e.target.value)}
                      className={validationErrors.transfers?.[index]?.selectedInventoryId ? 'error' : ''}
                      disabled={loading}
                    >
                      <option value="">Seleccionar donación</option>
                      {categoryInventory.map(item => (
                        <option key={item.id} value={item.id}>
                          {item.description || item.category} (Disponible: {item.quantity})
                        </option>
                      ))}
                    </select>
                    {validationErrors.transfers?.[index]?.selectedInventoryId && (
                      <div className="field-error">
                        {validationErrors.transfers[index].selectedInventoryId}
                      </div>
                    )}
                    {categoryInventory.length === 0 && (
                      <div className="field-info">
                        No hay donaciones disponibles en esta categoría
                      </div>
                    )}
                  </div>

                  <div className="form-group">
                    <label htmlFor={`quantity-${index}`}>
                      Cantidad a transferir
                    </label>
                    <input
                      type="number"
                      id={`quantity-${index}`}
                      value={transfer.quantity}
                      onChange={(e) => handleTransferChange(index, 'quantity', e.target.value)}
                      placeholder="Cantidad"
                      min="1"
                      max={transfer.selectedInventoryId ? 
                        availableInventory.find(item => item.id.toString() === transfer.selectedInventoryId)?.quantity : 
                        undefined
                      }
                      className={validationErrors.transfers?.[index]?.quantity ? 'error' : ''}
                      disabled={loading || !transfer.selectedInventoryId}
                    />
                    {validationErrors.transfers?.[index]?.quantity && (
                      <div className="field-error">
                        {validationErrors.transfers[index].quantity}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
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
            {loading ? 'Transfiriendo...' : 'Transferir Donaciones'}
          </button>
        </div>
      </form>

      <div className="form-info">
        <h4>Información importante:</h4>
        <ul>
          <li>Solo puede transferir donaciones que tiene disponibles en su inventario</li>
          <li>La cantidad transferida se descontará automáticamente de su inventario</li>
          <li>La organización destino recibirá las donaciones en su inventario</li>
          <li>Esta acción no se puede deshacer</li>
        </ul>
      </div>
    </div>
  );
};

export default DonationTransferForm;