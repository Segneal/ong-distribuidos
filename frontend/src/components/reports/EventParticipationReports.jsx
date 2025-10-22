import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import {
  Search,
  ExpandMore,
  FilterList,
  Assessment,
  Event,
  Person
} from '@mui/icons-material';
import { useQuery } from '@apollo/client';
import { GET_EVENT_PARTICIPATION_REPORT, GET_USERS_LIST } from '../../graphql/events';
import { useAuth } from '../../contexts/AuthContext';
import EventFilters from './EventFilters';

const EventParticipationReports = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    fechaDesde: '',
    fechaHasta: '',
    usuarioId: user?.id || '',
    repartodonaciones: null
  });

  // Query para obtener lista de usuarios (solo para Presidentes y Coordinadores)
  const { data: usersData, loading: usersLoading } = useQuery(GET_USERS_LIST, {
    skip: !user || (user.rol !== 'PRESIDENTE' && user.rol !== 'COORDINADOR'),
    fetchPolicy: 'cache-and-network'
  });

  // Query para obtener datos de participación en eventos
  const { data, loading, error, refetch } = useQuery(GET_EVENT_PARTICIPATION_REPORT, {
    variables: {
      fechaDesde: filters.fechaDesde || undefined,
      fechaHasta: filters.fechaHasta || undefined,
      usuarioId: filters.usuarioId,
      repartodonaciones: filters.repartodonaciones
    },
    skip: !filters.usuarioId, // No ejecutar si no hay usuario seleccionado
    fetchPolicy: 'cache-and-network'
  });

  // Manejar cambios en filtros
  const handleFilterChange = useCallback((field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Aplicar filtros guardados
  const handleApplySavedFilter = useCallback((savedFilters) => {
    setFilters(savedFilters);
  }, []);

  // Limpiar filtros
  const handleClearFilters = () => {
    setFilters({
      fechaDesde: '',
      fechaHasta: '',
      usuarioId: user?.id || '',
      repartodonaciones: null
    });
  };

  // Formatear fecha para mostrar
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  // Formatear cantidad
  const formatQuantity = (quantity) => {
    return new Intl.NumberFormat('es-ES').format(quantity);
  };

  // Verificar permisos para selección de usuario
  const canSelectAnyUser = user?.role === 'PRESIDENTE' || user?.role === 'COORDINADOR';
  const availableUsers = usersData?.users || [];

  // Validar que usuario_id sea obligatorio
  const isUserRequired = !filters.usuarioId;

  if (loading && filters.usuarioId) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error al cargar los datos: {error.message}
      </Alert>
    );
  }

  const reportData = data?.eventParticipationReport || [];
  const totalEvents = reportData.reduce((sum, month) => sum + month.eventos.length, 0);
  const totalDonations = reportData.reduce((sum, month) => 
    sum + month.eventos.reduce((eventSum, event) => eventSum + event.donaciones.length, 0), 0
  );

  return (
    <Box>
      {/* Filtros guardados */}
      <EventFilters 
        currentFilters={filters}
        onApplyFilter={handleApplySavedFilter}
      />

      {/* Formulario de filtros */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterList />
          Filtros de Búsqueda
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="date"
              label="Fecha Desde"
              value={filters.fechaDesde}
              onChange={(e) => handleFilterChange('fechaDesde', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="date"
              label="Fecha Hasta"
              value={filters.fechaHasta}
              onChange={(e) => handleFilterChange('fechaHasta', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth required error={isUserRequired}>
              <InputLabel>Usuario *</InputLabel>
              <Select
                value={filters.usuarioId}
                label="Usuario *"
                onChange={(e) => handleFilterChange('usuarioId', e.target.value)}
                disabled={usersLoading || !canSelectAnyUser}
              >
                {canSelectAnyUser ? (
                  availableUsers.map(usuario => (
                    <MenuItem key={usuario.id} value={usuario.id}>
                      {usuario.nombre} ({usuario.rol})
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem value={user?.id || ''}>
                    {user?.nombre || 'Usuario actual'}
                  </MenuItem>
                )}
              </Select>
              {isUserRequired && (
                <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                  El usuario es obligatorio
                </Typography>
              )}
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Reparto de Donaciones</InputLabel>
              <Select
                value={filters.repartodonaciones === null ? '' : filters.repartodonaciones.toString()}
                label="Reparto de Donaciones"
                onChange={(e) => {
                  const value = e.target.value;
                  handleFilterChange('repartodonaciones', value === '' ? null : value === 'true');
                }}
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="true">Con reparto</MenuItem>
                <MenuItem value="false">Sin reparto</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<Search />}
            onClick={() => refetch()}
            disabled={isUserRequired}
          >
            Buscar
          </Button>
          <Button
            variant="outlined"
            onClick={handleClearFilters}
          >
            Limpiar Filtros
          </Button>
        </Box>

        {isUserRequired && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Debe seleccionar un usuario para generar el reporte.
          </Alert>
        )}
      </Paper>

      {/* Resumen general */}
      {reportData.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Assessment />
              Resumen de Participación
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Meses con Actividad
                </Typography>
                <Typography variant="h4">
                  {reportData.length}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Eventos
                </Typography>
                <Typography variant="h4">
                  {totalEvents}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Donaciones Asociadas
                </Typography>
                <Typography variant="h4">
                  {totalDonations}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Resultados agrupados por mes */}
      {!filters.usuarioId ? (
        <Alert severity="info">
          Seleccione un usuario para ver el reporte de participación en eventos.
        </Alert>
      ) : reportData.length === 0 ? (
        <Alert severity="info">
          No se encontraron eventos con los filtros aplicados.
        </Alert>
      ) : (
        <Box>
          {reportData.map((monthData, index) => (
            <Accordion key={monthData.mes} defaultExpanded={index === 0}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <Event />
                  <Typography variant="h6">
                    {monthData.mes}
                  </Typography>
                  <Box sx={{ ml: 'auto', display: 'flex', gap: 2 }}>
                    <Chip 
                      label={`${monthData.eventos.length} eventos`}
                      variant="outlined"
                      size="small"
                    />
                    <Chip 
                      label={`${monthData.eventos.reduce((sum, event) => sum + event.donaciones.length, 0)} donaciones`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  {monthData.eventos.map((evento, eventIndex) => (
                    <Box key={eventIndex} sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Typography variant="h6">
                          Día {evento.dia} - {evento.nombre}
                        </Typography>
                        <Chip 
                          label={`${evento.donaciones.length} donaciones`}
                          size="small"
                          color="secondary"
                        />
                      </Box>
                      
                      {evento.descripcion && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {evento.descripcion}
                        </Typography>
                      )}

                      {evento.donaciones.length > 0 ? (
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Categoría</TableCell>
                                <TableCell>Descripción</TableCell>
                                <TableCell align="right">Cantidad</TableCell>
                                <TableCell>Fecha Alta</TableCell>
                                <TableCell>Usuario Alta</TableCell>
                                <TableCell>Estado</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {evento.donaciones.map((donacion) => (
                                <TableRow key={donacion.id}>
                                  <TableCell>
                                    <Chip 
                                      label={donacion.categoria}
                                      size="small"
                                      variant="outlined"
                                    />
                                  </TableCell>
                                  <TableCell>
                                    {donacion.descripcion || '-'}
                                  </TableCell>
                                  <TableCell align="right">
                                    {formatQuantity(donacion.cantidad)}
                                  </TableCell>
                                  <TableCell>
                                    {formatDate(donacion.fechaAlta)}
                                  </TableCell>
                                  <TableCell>
                                    {donacion.usuarioAlta?.nombre || '-'}
                                  </TableCell>
                                  <TableCell>
                                    <Chip 
                                      label={donacion.eliminado ? 'Eliminado' : 'Activo'}
                                      color={donacion.eliminado ? 'error' : 'success'}
                                      size="small"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Alert severity="info" sx={{ mt: 1 }}>
                          No hay donaciones asociadas a este evento.
                        </Alert>
                      )}
                      
                      {eventIndex < monthData.eventos.length - 1 && (
                        <Divider sx={{ mt: 2 }} />
                      )}
                    </Box>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default EventParticipationReports;