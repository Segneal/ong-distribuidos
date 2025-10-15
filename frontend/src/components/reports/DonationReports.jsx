import React, { useState, useEffect } from 'react';
import { useQuery } from '@apollo/client';
import {
  Box,
  Paper,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import DonationFilters from './DonationFilters';
import DonationResults from './DonationResults';
import SavedFilters from './SavedFilters';
import ExcelExport from './ExcelExport';
import { DONATION_REPORT_QUERY } from '../../graphql/queries/donationQueries';
import { useAuth } from '../../hooks/useAuth';

const DonationReports = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    categoria: null,
    fechaDesde: null,
    fechaHasta: null,
    eliminado: null
  });
  const [appliedFilters, setAppliedFilters] = useState(null);

  // Check if user has permission (Presidente or Vocal)
  const hasPermission = user && (user.rol === 'Presidente' || user.rol === 'Vocal');

  const { data, loading, error, refetch } = useQuery(DONATION_REPORT_QUERY, {
    variables: appliedFilters,
    skip: !appliedFilters || !hasPermission,
    errorPolicy: 'all'
  });

  const handleApplyFilters = (newFilters) => {
    setAppliedFilters(newFilters);
  };

  const handleLoadSavedFilter = (savedFilter) => {
    const filterConfig = JSON.parse(savedFilter.configuracion);
    setFilters(filterConfig);
    setAppliedFilters(filterConfig);
  };

  if (!hasPermission) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          No tienes permisos para acceder a los reportes de donaciones. 
          Solo los Presidentes y Vocales pueden ver esta información.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Reportes de Donaciones
      </Typography>

      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Filters Section */}
        <Paper sx={{ p: 3, flex: '1 1 400px', minWidth: 400 }}>
          <Typography variant="h6" gutterBottom>
            Filtros
          </Typography>
          
          <DonationFilters
            filters={filters}
            onFiltersChange={setFilters}
            onApplyFilters={handleApplyFilters}
          />

          <Box sx={{ mt: 3 }}>
            <SavedFilters
              filterType="DONACIONES"
              onLoadFilter={handleLoadSavedFilter}
              currentFilters={filters}
            />
          </Box>
        </Paper>

        {/* Results Section */}
        <Paper sx={{ p: 3, flex: '2 1 600px', minWidth: 600 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Resultados
            </Typography>
            {data && data.donationReport && (
              <ExcelExport filters={appliedFilters} />
            )}
          </Box>

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Error al cargar los datos: {error.message}
            </Alert>
          )}

          {!appliedFilters && !loading && (
            <Alert severity="info">
              Configura los filtros y haz clic en "Aplicar Filtros" para ver los resultados.
            </Alert>
          )}

          {data && data.donationReport && (
            <DonationResults data={data.donationReport} />
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default DonationReports;