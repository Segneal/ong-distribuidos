import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
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
import { SAVED_DONATION_FILTERS_QUERY } from '../../graphql/queries/donationQueries';
import {
  SAVE_DONATION_FILTER_MUTATION,
  UPDATE_DONATION_FILTER_MUTATION,
  DELETE_DONATION_FILTER_MUTATION
} from '../../graphql/mutations/filterMutations';
import { formatDate } from '../../utils/helpers';

const SavedFilters = ({ filterType, onLoadFilter, currentFilters }) => {
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [editingFilter, setEditingFilter] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState(null);

  const { data, loading, error, refetch } = useQuery(SAVED_DONATION_FILTERS_QUERY, {
    errorPolicy: 'all'
  });

  const [saveDonationFilter] = useMutation(SAVE_DONATION_FILTER_MUTATION, {
    onCompleted: () => {
      setSaveDialogOpen(false);
      setFilterName('');
      refetch();
    }
  });

  const [updateDonationFilter] = useMutation(UPDATE_DONATION_FILTER_MUTATION, {
    onCompleted: () => {
      setEditDialogOpen(false);
      setEditingFilter(null);
      setFilterName('');
      refetch();
    }
  });

  const [deleteDonationFilter] = useMutation(DELETE_DONATION_FILTER_MUTATION, {
    onCompleted: () => {
      refetch();
    }
  });

  const handleSaveFilter = async () => {
    if (!filterName.trim()) return;

    try {
      await saveDonationFilter({
        variables: {
          nombre: filterName.trim(),
          filtros: currentFilters
        }
      });
    } catch (err) {
      console.error('Error saving filter:', err);
    }
  };

  const handleEditFilter = async () => {
    if (!filterName.trim() || !editingFilter) return;

    try {
      await updateDonationFilter({
        variables: {
          id: editingFilter.id,
          nombre: filterName.trim(),
          filtros: currentFilters
        }
      });
    } catch (err) {
      console.error('Error updating filter:', err);
    }
  };

  const handleDeleteFilter = async (filterId) => {
    try {
      await deleteDonationFilter({
        variables: { id: filterId }
      });
    } catch (err) {
      console.error('Error deleting filter:', err);
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

  const hasCurrentFilters = currentFilters && Object.values(currentFilters).some(value => value !== null && value !== '');

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Filtros Guardados
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
        <Alert severity="error" sx={{ mb: 2 }}>
          Error al cargar filtros guardados: {error.message}
        </Alert>
      )}

      {data && data.savedDonationFilters && (
        <List dense>
          {data.savedDonationFilters.length === 0 ? (
            <ListItem>
              <ListItemText
                primary="No hay filtros guardados"
                secondary="Configura algunos filtros y guárdalos para uso futuro"
              />
            </ListItem>
          ) : (
            data.savedDonationFilters.map((filter) => (
              <ListItem
                key={filter.id}
                button
                onClick={() => onLoadFilter(filter)}
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
                        <Chip label={filterType} size="small" variant="outlined" />
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
      )}

      {/* Save Filter Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Guardar Filtro</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nombre del filtro"
            fullWidth
            variant="outlined"
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            placeholder="Ej: Donaciones de alimentos del último mes"
          />
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
        <DialogTitle>Editar Filtro</DialogTitle>
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

export default SavedFilters;