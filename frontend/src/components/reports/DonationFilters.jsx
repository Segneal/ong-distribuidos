import React, { useState } from 'react';
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
  AccordionDetails,
  Grid
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
import { useQuery, useMutation } from '@apollo/client';
import {
  GET_SAVED_DONATION_FILTERS,
  SAVE_DONATION_FILTER,
  UPDATE_DONATION_FILTER,
  DELETE_DONATION_FILTER
} from '../../graphql/donations';

const DonationFilters = ({ currentFilters, onApplyFilter }) => {
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [editingFilter, setEditingFilter] = useState(null);
  const [error, setError] = useState(null);

  // Query para obtener filtros guardados
  const { data, loading, refetch } = useQuery(GET_SAVED_DONATION_FILTERS, {
    fetchPolicy: 'cache-and-network'
  });

  // Mutations
  const [saveDonationFilter, { loading: saving }] = useMutation(SAVE_DONATION_FILTER, {
    onCompleted: () => {
      setSaveDialogOpen(false);
      setFilterName('');
      setError(null);
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });

  const [updateDonationFilter, { loading: updating }] = useMutation(UPDATE_DONATION_FILTER, {
    onCompleted: () => {
      setEditDialogOpen(false);
      setEditingFilter(null);
      setFilterName('');
      setError(null);
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });

  const [deleteDonationFilter, { loading: deleting }] = useMutation(DELETE_DONATION_FILTER, {
    onCompleted: () => {
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });

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
  const handleConfirmSave = () => {
    if (!filterName.trim()) {
      setError('El nombre del filtro es obligatorio');
      return;
    }

    saveDonationFilter({
      variables: {
        nombre: filterName.trim(),
        filtros: currentFilters
      }
    });
  };

  // Manejar editar filtro
  const handleEditFilter = (filter) => {
    setEditingFilter(filter);
    setFilterName(filter.nombre);
    setEditDialogOpen(true);
    setError(null);
  };

  // Confirmar editar filtro
  const handleConfirmEdit = () => {
    if (!filterName.trim()) {
      setError('El nombre del filtro es obligatorio');
      return;
    }

    updateDonationFilter({
      variables: {
        id: editingFilter.id,
        nombre: filterName.trim(),
        filtros: editingFilter.filtros
      }
    });
  };

  // Manejar eliminar filtro
  const handleDeleteFilter = (filterId) => {
    if (window.confirm('¿Está seguro de que desea eliminar este filtro?')) {
      deleteDonationFilter({
        variables: { id: filterId }
      });
    }
  };

  // Aplicar filtro guardado
  const handleApplyFilter = (filter) => {
    onApplyFilter(filter.filtros);
  };

  // Formatear filtros para mostrar
  const formatFilterDisplay = (filtros) => {
    const parts = [];
    
    if (filtros.categoria) {
      parts.push(`Categoría: ${filtros.categoria}`);
    }
    
    if (filtros.fechaDesde) {
      parts.push(`Desde: ${new Date(filtros.fechaDesde).toLocaleDateString('es-ES')}`);
    }
    
    if (filtros.fechaHasta) {
      parts.push(`Hasta: ${new Date(filtros.fechaHasta).toLocaleDateString('es-ES')}`);
    }
    
    if (filtros.eliminado !== null && filtros.eliminado !== undefined) {
      parts.push(`Estado: ${filtros.eliminado ? 'Eliminados' : 'Activos'}`);
    }
    
    return parts.length > 0 ? parts.join(' | ') : 'Sin filtros específicos';
  };

  const savedFilters = data?.savedDonationFilters || [];

  return (
    <Box sx={{ mb: 3 }}>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Bookmark />
            <Typography variant="h6">
              Filtros Guardados ({savedFilters.length})
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
                No tienes filtros guardados. Aplica algunos filtros y guárdalos para reutilizarlos fácilmente.
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
        <DialogTitle>Guardar Filtro</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Nombre del filtro"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)}
              placeholder="Ej: Donaciones de alimentos del último mes"
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
        <DialogTitle>Editar Filtro</DialogTitle>
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

export default DonationFilters;