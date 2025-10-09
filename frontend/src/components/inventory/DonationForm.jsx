import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const DonationForm = ({ donation, onSuccess }) => {
  const [formData, setFormData] = useState({
    category: '',
    description: '',
    quantity: ''
  });
  const [createdByUser, setCreatedByUser] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const { user } = useAuth();

  const categories = [
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  // Cargar datos si estamos editando
  useEffect(() => {
    if (donation) {
      setFormData({
        category: donation.category || '',
        description: donation.description || '',
        quantity: donation.quantity?.toString() || ''
      });
      
      // Obtener nombre del usuario que creó la donación
      if (donation.createdBy) {
        fetchUserName(donation.createdBy);
      }
    }
  }, [donation]);

  const fetchUserName = async (userId) => {
    try {
      const response = await api.get(`/users/${userId}`);
      if (response.data.success && response.data.user) {
        const user = response.data.user;
        setCreatedByUser(`${user.firstName} ${user.lastName}`.trim() || user.username);
      } else {
        setCreatedByUser(`Usuario ID: ${userId}`);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      setCreatedByUser(`Usuario ID: ${userId}`);
    }
  };

  const validateForm = () => {
    const errors = {};

    // Validar categoría
    if (!formData.category) {
      errors.category = 'La categoría es obligatoria';
    }

    // Validar cantidad
    if (!formData.quantity) {
      errors.quantity = 'La cantidad es obligatoria';
    } else {
      const quantity = parseInt(formData.quantity);
      if (isNaN(quantity)) {
        errors.quantity = 'La cantidad debe ser un número';
      } else if (quantity < 0) {
        errors.quantity = 'La cantidad no puede ser negativa';
      } else if (quantity === 0) {
        errors.quantity = 'La cantidad debe ser mayor a cero';
      }
    }

    // Validar descripción (opcional pero si se proporciona, debe tener contenido)
    if (formData.description && formData.description.trim().length === 0) {
      errors.description = 'La descripción no puede estar vacía si se proporciona';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Limpiar error de validación cuando el usuario empiece a escribir
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
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
      const submitData = {
        category: formData.category,
        description: formData.description.trim() || null,
        quantity: parseInt(formData.quantity)
      };

      let response;
      if (donation) {
        // Actualizar donación existente
        response = await api.put(`/inventory/${donation.id}`, submitData);
      } else {
        // Crear nueva donación
        response = await api.post('/inventory', submitData);
      }

      if (response.data.success) {
        onSuccess && onSuccess();
      } else {
        setError(response.data.error || 'Error al guardar donación');
      }
    } catch (err) {
      console.error('Error al guardar donación:', err);
      setError(err.response?.data?.error || 'Error al guardar donación');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (donation) {
      // Si estamos editando, restaurar valores originales
      setFormData({
        category: donation.category || '',
        description: donation.description || '',
        quantity: donation.quantity?.toString() || ''
      });
    } else {
      // Si es nuevo, limpiar formulario
      setFormData({
        category: '',
        description: '',
        quantity: ''
      });
    }
    setValidationErrors({});
    setError('');
  };

  const getCategoryLabel = (categoryValue) => {
    const category = categories.find(c => c.value === categoryValue);
    return category ? category.label : categoryValue;
  };

  return (
    <div className="donation-form">
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Información de la donación existente */}
        {donation && (
          <div className="donation-info">
            <div className="info-item">
              <strong>Fecha de alta:</strong> {new Date(donation.createdAt).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
            {donation.createdBy && (
              <div className="info-item">
                <strong>Creado por:</strong> {createdByUser || `Usuario ID: ${donation.createdBy}`}
              </div>
            )}
          </div>
        )}

        {/* Categoría */}
        <div className="form-group">
          <label htmlFor="category">
            Categoría <span className="required">*</span>
            {donation && <span className="field-note"> (No modificable)</span>}
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleInputChange}
            className={validationErrors.category ? 'error' : ''}
            disabled={loading || donation} // Deshabilitar si estamos editando
          >
            <option value="">Seleccionar categoría</option>
            {categories.map(category => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
          {validationErrors.category && (
            <div className="field-error">{validationErrors.category}</div>
          )}
        </div>

        {/* Descripción */}
        <div className="form-group">
          <label htmlFor="description">Descripción</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Descripción detallada de la donación (opcional)"
            rows="3"
            className={validationErrors.description ? 'error' : ''}
            disabled={loading}
          />
          {validationErrors.description && (
            <div className="field-error">{validationErrors.description}</div>
          )}
        </div>

        {/* Cantidad */}
        <div className="form-group">
          <label htmlFor="quantity">
            Cantidad <span className="required">*</span>
          </label>
          <input
            type="number"
            id="quantity"
            name="quantity"
            value={formData.quantity}
            onChange={handleInputChange}
            placeholder="Cantidad de elementos"
            min="1"
            className={validationErrors.quantity ? 'error' : ''}
            disabled={loading}
          />
          {validationErrors.quantity && (
            <div className="field-error">{validationErrors.quantity}</div>
          )}
        </div>



        {/* Botones */}
        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleReset}
            disabled={loading}
          >
            {donation ? 'Restaurar' : 'Limpiar'}
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : (donation ? 'Actualizar' : 'Crear')}
          </button>
        </div>
      </form>

      {/* Ayuda */}
      <div className="form-help">
        <h4>Información importante:</h4>
        <ul>
          <li>La categoría es obligatoria y no se puede cambiar después de crear la donación</li>
          <li>La cantidad debe ser un número positivo</li>
          <li>La descripción es opcional pero recomendada para mejor identificación</li>
          {donation && (
            <li>Solo se pueden modificar la descripción y la cantidad</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default DonationForm;