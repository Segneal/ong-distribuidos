import React, { useState } from 'react';
import './Inscriptions.css';

const InscriptionRequestForm = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    email: '',
    telefono: '',
    organizacion_destino: '',
    rol_solicitado: 'VOLUNTARIO',
    mensaje: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const organizaciones = [
    { id: 'empuje-comunitario', name: 'Empuje Comunitario' },
    { id: 'fundacion-esperanza', name: 'Fundación Esperanza' },
    { id: 'ong-solidaria', name: 'ONG Solidaria' },
    { id: 'centro-comunitario', name: 'Centro Comunitario Unidos' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/messaging/inscription-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        onSuccess && onSuccess(data);
        onClose && onClose();
      } else {
        setError(data.error || 'Error al enviar solicitud');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="inscription-form-overlay">
      <div className="inscription-form-modal">
        <div className="inscription-form-header">
          <h2>Solicitud de Inscripción</h2>
          <button 
            className="close-button"
            onClick={onClose}
            disabled={loading}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="inscription-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nombre">Nombre *</label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="apellido">Apellido *</label>
              <input
                type="text"
                id="apellido"
                name="apellido"
                value={formData.apellido}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="telefono">Teléfono</label>
              <input
                type="tel"
                id="telefono"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                disabled={loading}
                placeholder="+54911234567"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="organizacion_destino">Organización *</label>
              <select
                id="organizacion_destino"
                name="organizacion_destino"
                value={formData.organizacion_destino}
                onChange={handleChange}
                required
                disabled={loading}
              >
                <option value="">Seleccionar organización</option>
                {organizaciones.map(org => (
                  <option key={org.id} value={org.id}>
                    {org.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="rol_solicitado">Rol Solicitado *</label>
              <select
                id="rol_solicitado"
                name="rol_solicitado"
                value={formData.rol_solicitado}
                onChange={handleChange}
                required
                disabled={loading}
              >
                <option value="VOLUNTARIO">Voluntario</option>
                <option value="COORDINADOR">Coordinador</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="mensaje">Mensaje de Presentación</label>
            <textarea
              id="mensaje"
              name="mensaje"
              value={formData.mensaje}
              onChange={handleChange}
              disabled={loading}
              rows="4"
              placeholder="Cuéntanos por qué quieres unirte a esta organización..."
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="cancel-button"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Enviando...' : 'Enviar Solicitud'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InscriptionRequestForm;