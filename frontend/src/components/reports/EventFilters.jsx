import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Save,
  Edit,
  Delete,
  ExpandMore,
  BookmarkBorder,
  Bookmark,
  FilterList
} from '@mui/icons-material';
import axios from 'axios';
import { getAuthHeaders, API_ENDPOINTS } from '../../config/api';

const EventFilters = ({ currentFilters, onApplyFilter }) => {
  const [savedFilters, setSavedFilters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [editingFilter, setEditingFilter] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Cargar filtros guardados al montar el componente
  useEffect(() => {
    loadSavedFilters();
  }, []);

  // Función para cargar filtros guardados
  const loadSavedFilters = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}${API_ENDPOINTS.FILTERS.EVENTS}`,
        { headers: getAuthHeaders() }
      );
      
      setSavedFilters(response.data || []);
    } catch (error) {
      console.error('Error al cargar filtros guardados:', error);
      setError('Error al cargar los filtros guardados');
    } finally {
      setLoading(false);
    }
  };

  // Manejar guardar filtro actual
  const handleSaveCurrentFilter = () => {
    // Verificar que hay filtros aplicados
    const hasFilters = Object.values(currentFilters).some(value => 
      value !== '' && value !== null && value !== undefined
    );
    
    if (!hasFilters) {
      setError('No hay filtros aplicados para guardar');
      return;
    }
    
    setSaveDialogOpen(true);
    setError(null);
  };

  // Confirmar guardar filtro
  const handleConfirmSave = async () => {
    if (!filterName.trim()) {
      setError('El nombre del filtro es obligatorio');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}${API_ENDPOINTS.FILTERS.EVENTS}`,
        {
          nombre: filterName.trim(),
          filtros: currentFilters
        },
        { headers: getAuthHeaders() }
      );

      setSaveDialogOpen(false);
      setFilterName('');
      await loadSavedFilters(); // Recargar la lista
    } catch (error) {
      console.error('Error al guardar filtro:', error);
      setError(error.response?.data?.error || 'Error al guardar el filtro');
    } finally {
      setSaving(false);
    }
  };

  // Manejar editar filtro
  const handleEditFilter = (filter) => {
    setEditingFilter(filter);
    setFilterName(filter.nombre);
    setEditDialogOpen(true);
    setError(null);
  };

  // Confirmar editar filtro
  const handleConfirmEdit = async () => {
    if (!filterName.trim()) {
      setError('El nombre del filtro es obligatorio');
      return;
    }

    try {
      setUpdating(true);
      setError(null);

      await axios.put(
        `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}${API_ENDPOINTS.FILTERS.EVENTS}/${editingFilter.id}`,
        {
          nombre: filterName.trim(),
          filtros: editingFilter.filtros
        },
        { headers: getAuthHeaders() }
      );

      setEditDialogOpen(false);
      setEditingFilter(null);
      setFilterName('');
      await loadSavedFilters(); // Recargar la lista
    } catch (error) {
      console.error('Error al actualizar filtro:', error);
      setError(error.response?.data?.error || 'Error al actualizar el filtro');
    } finally {
      setUpdating(false);
    }
  };

  // Manejar eliminar filtro
  const handleDeleteFilter = async (filterId) => {
    if (!window.confirm('¿Está seguro de que desea eliminar este filtro?')) {
      return;
    }

    try {
      setDeleting(true);
      setError(null);

      await axios.delete(
        `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}${API_ENDPOINTS.FILTERS.EVENTS}/${filterId}`,
        { headers: getAuthHeaders() }
      );

      await loadSavedFilters(); // Recargar la lista
    } catch (error) {
      console.error('Error al eliminar filtro:', error);
      setError(error.response?.data?.error || 'Error al eliminar el filtro');
    } finally {
      setDeleting(false);
    }
  };

  // Aplicar filtro guardado
  const handleApplyFilter = (filter) => {
    onApplyFilter(filter.filtros);
  };

  // Formatear filtros para mostrar
  const formatFilterDisplay = (filtros) => {
    const parts = [];
    
    if (filtros.fechaDesde) {
      parts.push(`Desde: ${new Date(filtros.fechaDesde).toLocaleDateString('es-ES')}`);
    }
    
    if (filtros.fechaHasta) {
      parts.push(`Hasta: ${new Date(filtros.fechaHasta).toLocaleDateString('es-ES')}`);
    }
    
    if (filtros.usuarioId) {
      parts.push(`Usuario: ${filtros.usuarioId}`);
    }
    
    if (filtros.repartodonaciones !== null && filtros.repartodonaciones !== undefined) {
      parts.push(`Reparto: ${filtros.repartodonaciones ? 'Con reparto' : 'Sin reparto'}`);
    }
    
    return parts.length > 0 ? parts.join(' | ') : 'Sin filtros específicos';
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Bookmark />
            <Typography variant="h6">
              Filtros de Eventos Guardados ({savedFilters.length})
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            {/* Botón para guardar filtro actual */}
            <Box sx={{ mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Save />}
                onClick={handleSaveCurrentFilter}
                disabled={saving}
              >
                Guardar Filtro Actual
              </Button>
            </Box>

            {/* Lista de filtros guardados */}
            {loading ? (
              <Box display="flex" justifyContent="center" p={2}>
                <CircularProgress />
              </Box>
            ) : savedFilters.length === 0 ? (
              <Alert severity="info">
                No tienes filtros de eventos guardados. Aplica algunos filtros y guárdalos para reutilizarlos fácilmente.
              </Alert>
            ) : (
              <List>
                {savedFilters.map((filter) => (
                  <ListItem key={filter.id} divider>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1">
                            {filter.nombre}
                          </Typography>
                          <Chip 
                            size="small" 
                            label={new Date(filter.fechaCreacion).toLocaleDateString('es-ES')}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={formatFilterDisplay(filter.filtros)}
                    />
                    <ListItemSecondaryAction>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => handleApplyFilter(filter)}
                          startIcon={<FilterList />}
                        >
                          Aplicar
                        </Button>
                        <IconButton
                          size="small"
                          onClick={() => handleEditFilter(filter)}
                          disabled={updating}
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteFilter(filter.id)}
                          disabled={deleting}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Dialog para guardar filtro */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Guardar Filtro de Eventos</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Nombre del filtro"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)}
              placeholder="Ej: Eventos del último trimestre con reparto"
              autoFocus
            />
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Filtros que se guardarán:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatFilterDisplay(currentFilters)}
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>
            Cancelar
          </Button>
          <Button 
            onClick={handleConfirmSave} 
            variant="contained"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} /> : <Save />}
          >
            {saving ? 'Guardando...' : 'Guardar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para editar filtro */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Filtro de Eventos</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Nombre del filtro"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)}
              autoFocus
            />
            
            {editingFilter && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Configuración del filtro:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatFilterDisplay(editingFilter.filtros)}
                </Typography>
              </Box>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>
            Cancelar
          </Button>
          <Button 
            onClick={handleConfirmEdit} 
            variant="contained"
            disabled={updating}
            startIcon={updating ? <CircularProgress size={20} /> : <Edit />}
          >
            {updating ? 'Actualizando...' : 'Actualizar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EventFilters;