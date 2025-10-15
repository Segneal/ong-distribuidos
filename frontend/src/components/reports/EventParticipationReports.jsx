import React, { useState, useEffect } from 'react';
import { useQuery } from '@apollo/client';
import {
  Box,
  Paper,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import EventFilters from './EventFilters';
import EventResults from './EventResults';
import EventSavedFilters from './EventSavedFilters';
import { EVENT_PARTICIPATION_REPORT_QUERY, USERS_QUERY } from '../../graphql/queries/eventQueries';
import { useAuth } from '../../hooks/useAuth';

const EventParticipationReports = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    fechaDesde: null,
    fechaHasta: null,
    usuarioId: user?.id || null,
    repartodonaciones: null
  });
  const [appliedFilters, setAppliedFilters] = useState(null);

  // Check if user can select other users (Presidente or Coordinador)
  const canSelectOtherUsers = user && (user.rol === 'Presidente' || user.rol === 'Coordinador');

  // Query for users list (only if user has permission)
  const { data: usersData, loading: usersLoading } = useQuery(USERS_QUERY, {
    skip: !canSelectOtherUsers,
    errorPolicy: 'all'
  });

  // Query for event participation report
  const { data, loading, error, refetch } = useQuery(EVENT_PARTICIPATION_REPORT_QUERY, {
    variables: appliedFilters,
    skip: !appliedFilters || !appliedFilters.usuarioId,
    errorPolicy: 'all'
  });

  // Set default user filter if user cannot select others
  useEffect(() => {
    if (!canSelectOtherUsers && user?.id) {
      setFilters(prev => ({
        ...prev,
        usuarioId: user.id
      }));
    }
  }, [user, canSelectOtherUsers]);

  const handleApplyFilters = (newFilters) => {
    // Validate that usuarioId is required
    if (!newFilters.usuarioId) {
      return;
    }
    setAppliedFilters(newFilters);
  };

  const handleLoadSavedFilter = (savedFilter) => {
    const filterConfig = JSON.parse(savedFilter.configuracion);
    
    // If user cannot select others, force their own ID
    if (!canSelectOtherUsers) {
      filterConfig.usuarioId = user.id;
    }
    
    setFilters(filterConfig);
    if (filterConfig.usuarioId) {
      setAppliedFilters(filterConfig);
    }
  };

  const handleUserChange = (usuarioId) => {
    const newFilters = {
      ...filters,
      usuarioId
    };
    setFilters(newFilters);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Reportes de Participación en Eventos
      </Typography>

      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Filters Section */}
        <Paper sx={{ p: 3, flex: '1 1 400px', minWidth: 400 }}>
          <Typography variant="h6" gutterBottom>
            Filtros
          </Typography>

          {/* User Selection - Required Field */}
          <Box sx={{ mb: 3 }}>
            {canSelectOtherUsers ? (
              <FormControl fullWidth required>
                <InputLabel>Usuario *</InputLabel>
                <Select
                  value={filters.usuarioId || ''}
                  label="Usuario *"
                  onChange={(e) => handleUserChange(e.target.value)}
                  disabled={usersLoading}
                >
                  {usersData?.users?.map((user) => (
                    <MenuItem key={user.id} value={user.id}>
                      {user.nombre} ({user.rol})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <Alert severity="info" sx={{ mb: 2 }}>
                Viendo reportes para: <strong>{user?.nombre}</strong>
                <br />
                <Typography variant="caption">
                  Solo los Presidentes y Coordinadores pueden ver reportes de otros usuarios.
                </Typography>
              </Alert>
            )}
          </Box>
          
          <EventFilters
            filters={filters}
            onFiltersChange={setFilters}
            onApplyFilters={handleApplyFilters}
            userRequired={true}
          />

          <Box sx={{ mt: 3 }}>
            <EventSavedFilters
              onLoadFilter={handleLoadSavedFilter}
              currentFilters={filters}
              canSelectOtherUsers={canSelectOtherUsers}
              currentUserId={user?.id}
            />
          </Box>
        </Paper>

        {/* Results Section */}
        <Paper sx={{ p: 3, flex: '2 1 600px', minWidth: 600 }}>
          <Typography variant="h6" gutterBottom>
            Resultados
          </Typography>

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
              Selecciona un usuario y configura los filtros, luego haz clic en "Aplicar Filtros" para ver los resultados.
            </Alert>
          )}

          {!filters.usuarioId && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Debes seleccionar un usuario para generar el reporte.
            </Alert>
          )}

          {data && data.eventParticipationReport && (
            <EventResults 
              data={data.eventParticipationReport}
              selectedUser={usersData?.users?.find(u => u.id === filters.usuarioId) || user}
            />
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default EventParticipationReports;