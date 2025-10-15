import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  TextField,
  Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { es } from 'date-fns/locale';

const EventFilters = ({ filters, onFiltersChange, onApplyFilters, userRequired = false }) => {
  const handleFilterChange = (field, value) => {
    const newFilters = {
      ...filters,
      [field]: value
    };
    onFiltersChange(newFilters);
  };

  const handleApply = () => {
    // Validate required fields
    if (userRequired && !filters.usuarioId) {
      return;
    }

    // Convert dates to ISO strings for GraphQL
    const processedFilters = {
      ...filters,
      fechaDesde: filters.fechaDesde ? filters.fechaDesde.toISOString() : null,
      fechaHasta: filters.fechaHasta ? filters.fechaHasta.toISOString() : null
    };
    onApplyFilters(processedFilters);
  };

  const handleClear = () => {
    const clearedFilters = {
      fechaDesde: null,
      fechaHasta: null,
      usuarioId: filters.usuarioId, // Keep user selection
      repartodonaciones: null
    };
    onFiltersChange(clearedFilters);
  };

  const canApply = !userRequired || filters.usuarioId;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
      <Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <DatePicker
              label="Fecha Desde"
              value={filters.fechaDesde}
              onChange={(date) => handleFilterChange('fechaDesde', date)}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <DatePicker
              label="Fecha Hasta"
              value={filters.fechaHasta}
              onChange={(date) => handleFilterChange('fechaHasta', date)}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Estado de Reparto de Donaciones</InputLabel>
              <Select
                value={filters.repartodonaciones !== null ? filters.repartodonaciones.toString() : ''}
                label="Estado de Reparto de Donaciones"
                onChange={(e) => {
                  const value = e.target.value;
                  handleFilterChange('repartodonaciones', value === '' ? null : value === 'true');
                }}
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="true">Con reparto de donaciones</MenuItem>
                <MenuItem value="false">Sin reparto de donaciones</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {userRequired && !filters.usuarioId && (
            <Grid item xs={12}>
              <Alert severity="warning">
                Debes seleccionar un usuario antes de aplicar los filtros.
              </Alert>
            </Grid>
          )}

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleApply}
                fullWidth
                disabled={!canApply}
              >
                Aplicar Filtros
              </Button>
              <Button
                variant="outlined"
                onClick={handleClear}
                fullWidth
              >
                Limpiar
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </LocalizationProvider>
  );
};

export default EventFilters;