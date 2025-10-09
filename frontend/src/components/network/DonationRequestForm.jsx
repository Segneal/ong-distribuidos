import React, { useState } from 'react';
import { messagingService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const DonationRequestForm = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    donations: [{ category: '', description: '' }]
  });
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

  const validateForm = () => {
    const errors = {};

    // Validar que hay al menos una donación
    if (!formData.donations || formData.donations.length === 0) {
      errors.donations = 'Debe agregar al menos una donación solicitada';
      setValidationErrors(errors);
      return false;
    }

    // Validar cada donación
    const donationErrors = [];
    formData.donations.forEach((donation, index) => {
      const donationError = {};
      
      if (!donation.category) {
        donationError.category = 'La categoría es obligatoria';
      }
      
      if (!donation.description || donation.description.trim().length === 0) {
        donationError.description = 'La descripción es obligatoria';
      }
      
      if (Object.keys(donationError).length > 0) {
        donationErrors[index] = donationError;
      }
    });

    if (donationErrors.length > 0) {
      errors.donations = donationErrors;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleDonationChange = (index, field, value) => {
    const newDonations = [...formData.donations];
    newDonations[index] = {
      ...newDonations[index],
      [field]: value
    };
    
    setFormData(prev => ({
      ...prev,
      donations: newDonations
    }));

    // Limpiar errores de validación
    if (validationErrors.donations && validationErrors.donations[index]) {
      const newErrors = { ...validationErrors };
      if (newErrors.donations[index]) {
        delete newErrors.donations[index][field];
        if (Object.keys(newErrors.donations[index]).length === 0) {
          delete newErrors.donations[index];
        }
      }
      setValidationErrors(newErrors);
    }
  };

  const addDonation = () => {
    setFormData(prev => ({
      ...prev,
      donations: [...prev.donations, { category: '', description: '' }]
    }));
  };

  const removeDonation = (index) => {
    if (formData.donations.length > 1) {
      const newDonations = formData.donations.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        donations: newDonations
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
      const requestData = {
        donations: formData.donations.map(d => ({
          category: d.category,
          description: d.description.trim()
        }))
      };

      const response = await messagingService.createDonationRequest(requestData);

      if (response.data.success) {
        onSuccess && onSuccess();
      } else {
        setError(response.data.error || 'Error al crear solicitud de donación');
      }
    } catch (err) {
      console.error('Error al crear solicitud:', err);
      setError(err.response?.data?.error || 'Error al crear solicitud de donación');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLabel = (categoryValue) => {
    const category = categories.find(c => c.value === categoryValue);
    return category ? category.label : categoryValue;
  };

  return (
    <div className="donation-request-form">
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-section">
          <h4>Donaciones Solicitadas</h4>
          <p className="form-help">
            Especifique las donaciones que necesita su organización. 
            Estas solicitudes serán enviadas a toda la red de ONGs.
          </p>

          {formData.donations.map((donation, index) => (
            <div key={index} className="donation-item">
              <div className="donation-header">
                <h5>Donación {index + 1}</h5>
                {formData.donations.length > 1 && (
                  <button
                    type="button"
                    className="btn btn-sm btn-danger"
                    onClick={() => removeDonation(index)}
                    disabled={loading}
                  >
                    Eliminar
                  </button>
                )}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor={`category-${index}`}>
                    Categoría <span className="required">*</span>
                  </label>
                  <select
                    id={`category-${index}`}
                    value={donation.category}
                    onChange={(e) => handleDonationChange(index, 'category', e.target.value)}
                    className={validationErrors.donations?.[index]?.category ? 'error' : ''}
                    disabled={loading}
                  >
                    <option value="">Seleccionar categoría</option>
                    {categories.map(category => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                  {validationErrors.donations?.[index]?.category && (
                    <div className="field-error">
                      {validationErrors.donations[index].category}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label htmlFor={`description-${index}`}>
                    Descripción <span className="required">*</span>
                  </label>
                  <textarea
                    id={`description-${index}`}
                    value={donation.description}
                    onChange={(e) => handleDonationChange(index, 'description', e.target.value)}
                    placeholder="Describa específicamente lo que necesita"
                    rows="3"
                    className={validationErrors.donations?.[index]?.description ? 'error' : ''}
                    disabled={loading}
                  />
                  {validationErrors.donations?.[index]?.description && (
                    <div className="field-error">
                      {validationErrors.donations[index].description}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          <button
            type="button"
            className="btn btn-secondary"
            onClick={addDonation}
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
            {loading ? 'Enviando...' : 'Enviar Solicitud'}
          </button>
        </div>
      </form>

      <div className="form-info">
        <h4>Información importante:</h4>
        <ul>
          <li>Las solicitudes se envían a toda la red de ONGs</li>
          <li>Puede agregar múltiples tipos de donaciones en una sola solicitud</li>
          <li>Sea específico en las descripciones para mejores resultados</li>
          <li>Podrá dar de baja la solicitud en cualquier momento</li>
        </ul>
      </div>
    </div>
  );
};

export default DonationRequestForm;