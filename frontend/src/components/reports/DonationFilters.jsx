import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { es } from 'date-fns/locale';

const DONATION_CATEGORIES = [
  'ALIMENTOS',
  'ROPA',
  'MEDICAMENTOS',
  'JUGUETES',
  'LIBROS',
  'ELECTRODOMESTICOS',
  'MUEBLES',
  'OTROS'
];

const DonationFilters = ({ filters, onFiltersChange, onApplyFilters }) => {
  const handleFilterChange = (field, value) => {
    const newFilters = {
      ...filters,
      [field]: value
    };
    onFiltersChange(newFilters);
  };

  const handleApply = () => {
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
      categoria: null,
      fechaDesde: null,
      fechaHasta: null,
      eliminado: null
    };
    onFiltersChange(clearedFilters);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
      <Box>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Categoría</InputLabel>
              <Select
                value={filters.categoria || ''}
                label="Categoría"
                onChange={(e) => handleFilterChange('categoria', e.target.value || null)}
              >
                <MenuItem value="">Todas las categorías</MenuItem>
                {DONATION_CATEGORIES.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

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
              <InputLabel>Estado de Eliminado</InputLabel>
              <Select
                value={filters.eliminado !== null ? filters.eliminado.toString() : ''}
                label="Estado de Eliminado"
                onChange={(e) => {
                  const value = e.target.value;
                  handleFilterChange('eliminado', value === '' ? null : value === 'true');
                }}
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="false">No eliminados</MenuItem>
                <MenuItem value="true">Eliminados</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleApply}
                fullWidth
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

export default DonationFilters;