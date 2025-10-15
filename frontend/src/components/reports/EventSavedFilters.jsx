import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Save as SaveIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';
import axios from 'axios';
import { formatDate } from '../../utils/helpers';

const EventSavedFilters = ({ onLoadFilter, currentFilters, canSelectOtherUsers, currentUserId }) => {
  const [savedFilters, setSavedFilters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [editingFilter, setEditingFilter] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState(null);
  const [error, setError] = useState(null);

  // Load saved filters on component mount
  React.useEffect(() => {
    loadSavedFilters();
  }, []);

  const loadSavedFilters = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/filters/events', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setSavedFilters(response.data);
    } catch (err) {
      console.error('Error loading saved filters:', err);
      setError('Error al cargar filtros guardados');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveFilter = async () => {
    if (!filterName.trim()) return;

    // Prepare filters for saving
    const filtersToSave = { ...currentFilters };
    
    // If user cannot select others, ensure their ID is saved
    if (!canSelectOtherUsers) {
      filtersToSave.usuarioId = currentUserId;
    }

    try {
      await axios.post('/api/filters/events', {
        nombre: filterName.trim(),
        filtros: filtersToSave
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      setSaveDialogOpen(false);
      setFilterName('');
      loadSavedFilters();
    } catch (err) {
      console.error('Error saving filter:', err);
      setError('Error al guardar el filtro');
    }
  };

  const handleEditFilter = async () => {
    if (!filterName.trim() || !editingFilter) return;

    // Prepare filters for updating
    const filtersToSave = { ...currentFilters };
    
    // If user cannot select others, ensure their ID is saved
    if (!canSelectOtherUsers) {
      filtersToSave.usuarioId = currentUserId;
    }

    try {
      await axios.put(`/api/filters/events/${editingFilter.id}`, {
        nombre: filterName.trim(),
        filtros: filtersToSave
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      setEditDialogOpen(false);
      setEditingFilter(null);
      setFilterName('');
      loadSavedFilters();
    } catch (err) {
      console.error('Error updating filter:', err);
      setError('Error al actualizar el filtro');
    }
  };

  const handleDeleteFilter = async (filterId) => {
    try {
      await axios.delete(`/api/filters/events/${filterId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      loadSavedFilters();
    } catch (err) {
      console.error('Error deleting filter:', err);
      setError('Error al eliminar el filtro');
    }
  };

  const handleMenuClick = (event, filter) => {
    setAnchorEl(event.currentTarget);
    setSelectedFilter(filter);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedFilter(null);
  };

  const handleEditClick = () => {
    setEditingFilter(selectedFilter);
    setFilterName(selectedFilter.nombre);
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    handleDeleteFilter(selectedFilter.id);
    handleMenuClose();
  };

  const handleLoadFilter = (filter) => {
    const filterConfig = JSON.parse(filter.configuracion);
    
    // If user cannot select others, force their own ID
    if (!canSelectOtherUsers) {
      filterConfig.usuarioId = currentUserId;
    }
    
    onLoadFilter(filter);
  };

  const hasCurrentFilters = currentFilters && (
    currentFilters.fechaDesde || 
    currentFilters.fechaHasta || 
    currentFilters.repartodonaciones !== null
  ) && currentFilters.usuarioId;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Filtros de Eventos Guardados
        </Typography>
        <Button
          startIcon={<SaveIcon />}
          variant="outlined"
          size="small"
          onClick={() => setSaveDialogOpen(true)}
          disabled={!hasCurrentFilters}
        >
          Guardar Filtro Actual
        </Button>
      </Box>

      {loading && <Typography>Cargando filtros...</Typography>}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <List dense>
        {savedFilters.length === 0 ? (
          <ListItem>
            <ListItemText
              primary="No hay filtros guardados"
              secondary="Configura algunos filtros y guárdalos para uso futuro"
            />
          </ListItem>
        ) : (
          savedFilters.map((filter) => (
            <ListItem
              key={filter.id}
              button
              onClick={() => handleLoadFilter(filter)}
              sx={{ 
                border: 1, 
                borderColor: 'divider', 
                borderRadius: 1, 
                mb: 1,
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
            >
              <ListItemText
                primary={filter.nombre}
                secondary={
                  <Box>
                    <Typography variant="caption" display="block">
                      Creado: {formatDate(filter.fechaCreacion)}
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <Chip label="EVENTOS" size="small" variant="outlined" />
                    </Box>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMenuClick(e, filter);
                  }}
                >
                  <MoreVertIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))
        )}
      </List>

      {/* Save Filter Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Guardar Filtro de Eventos</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nombre del filtro"
            fullWidth
            variant="outlined"
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            placeholder="Ej: Eventos del último trimestre con donaciones"
          />
          {!canSelectOtherUsers && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Este filtro se guardará solo para tu usuario.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleSaveFilter} variant="contained" disabled={!filterName.trim()}>
            Guardar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Filter Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Filtro de Eventos</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nombre del filtro"
            fullWidth
            variant="outlined"
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleEditFilter} variant="contained" disabled={!filterName.trim()}>
            Actualizar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditClick}>
          <EditIcon sx={{ mr: 1 }} />
          Editar
        </MenuItem>
        <MenuItem onClick={handleDeleteClick} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Eliminar
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default EventSavedFilters;