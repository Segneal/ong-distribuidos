import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import DonationForm from './DonationForm';
import './Inventory.css';

const InventoryList = () => {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showDeleted, setShowDeleted] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingDonation, setEditingDonation] = useState(null);
  const { user } = useAuth();

  const categories = [
    { value: '', label: 'Todas las categorías' },
    { value: 'ROPA', label: 'Ropa' },
    { value: 'ALIMENTOS', label: 'Alimentos' },
    { value: 'JUGUETES', label: 'Juguetes' },
    { value: 'UTILES_ESCOLARES', label: 'Útiles Escolares' }
  ];

  const fetchDonations = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = new URLSearchParams();
      if (selectedCategory) {
        params.append('category', selectedCategory);
      }
      if (showDeleted) {
        params.append('includeDeleted', 'true');
      }

      const response = await api.get(`/inventory?${params.toString()}`);
      
      if (response.data.success) {
        setDonations(response.data.donations || []);
      } else {
        setError(response.data.error || 'Error al cargar donaciones');
      }
    } catch (err) {
      console.error('Error al cargar donaciones:', err);
      setError(err.response?.data?.error || 'Error al cargar donaciones');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDonations();
  }, [selectedCategory, showDeleted]);

  const handleEdit = (donation) => {
    setEditingDonation(donation);
    setShowForm(true);
  };

  const handleDelete = async (donationId) => {
    if (!window.confirm('¿Está seguro que desea eliminar esta donación?')) {
      return;
    }

    try {
      const response = await api.delete(`/inventory/${donationId}`);
      
      if (response.data.success) {
        await fetchDonations(); // Recargar la lista
      } else {
        setError(response.data.error || 'Error al eliminar donación');
      }
    } catch (err) {
      console.error('Error al eliminar donación:', err);
      setError(err.response?.data?.error || 'Error al eliminar donación');
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingDonation(null);
    fetchDonations(); // Recargar la lista después de crear/editar
  };

  const getCategoryLabel = (category) => {
    const cat = categories.find(c => c.value === category);
    return cat ? cat.label : category;
  };



  if (loading) {
    return (
      <div className="inventory-container">
        <div className="loading">Cargando inventario...</div>
      </div>
    );
  }

  return (
    <div className="inventory-container">
      <div className="inventory-header">
        <h2>Inventario de Donaciones</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(true)}
        >
          Nueva Donación
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Filtros */}
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

        <div className="filter-group">
          <label>
            <input
              type="checkbox"
              checked={showDeleted}
              onChange={(e) => setShowDeleted(e.target.checked)}
            />
            Mostrar eliminadas
          </label>
        </div>
      </div>

      {/* Lista de donaciones */}
      <div className="donations-list">
        {donations.length === 0 ? (
          <div className="no-donations">
            No hay donaciones {selectedCategory && `en la categoría ${getCategoryLabel(selectedCategory)}`}
          </div>
        ) : (
          <div className="donations-table">
            <table>
              <thead>
                <tr>
                  <th>Categoría</th>
                  <th>Descripción</th>
                  <th>Cantidad</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {donations.map(donation => (
                  <tr key={donation.id} className={donation.deleted ? 'deleted-row' : ''}>
                    <td>{getCategoryLabel(donation.category)}</td>
                    <td>{donation.description || 'Sin descripción'}</td>
                    <td>{donation.quantity}</td>
                    <td>
                      {!donation.deleted && (
                        <div className="actions">
                          <button
                            className="btn btn-sm btn-secondary"
                            onClick={() => handleEdit(donation)}
                          >
                            Editar
                          </button>
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() => handleDelete(donation.id)}
                          >
                            Eliminar
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal del formulario */}
      {showForm && (
        <DonationFormModal
          donation={editingDonation}
          onClose={handleFormClose}
        />
      )}
    </div>
  );
};

// Componente modal para el formulario
const DonationFormModal = ({ donation, onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{donation ? 'Editar Donación' : 'Nueva Donación'}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <DonationForm donation={donation} onSuccess={onClose} />
        </div>
      </div>
    </div>
  );
};



export default InventoryList;