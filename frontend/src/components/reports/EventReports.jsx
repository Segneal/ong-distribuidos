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
  TablePagination
} from '@mui/material';
import {
  Search,
  ExpandMore,
  FilterList,
  Assessment,
  Event
} from '@mui/icons-material';
import { useQuery } from '@apollo/client';
import { GET_EVENT_PARTICIPATION_REPORT } from '../../graphql/events';
import { useAuth } from '../../contexts/AuthContext';

const EventReports = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    usuarioId: user?.id || '', // Required field, defaults to current user
    fechaDesde: '',
    fechaHasta: '',
    repartodonaciones: '' // '' = both, 'true' = yes, 'false' = no
  });
  
  // Estado para paginación
  const [paginationState, setPaginationState] = useState({});
  
  // Check if user can see other users' reports
  const canViewAllUsers = user?.role === 'PRESIDENTE' || user?.role === 'COORDINADOR';
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Query para obtener datos de eventos
  const { data, loading, error, refetch } = useQuery(GET_EVENT_PARTICIPATION_REPORT, {
    variables: {
      usuarioId: parseInt(filters.usuarioId) || user?.id,
      fechaDesde: filters.fechaDesde || undefined,
      fechaHasta: filters.fechaHasta || undefined,
      repartodonaciones: filters.repartodonaciones === '' ? undefined : filters.repartodonaciones === 'true'
    },
    fetchPolicy: 'cache-and-network',
    skip: !filters.usuarioId && !user?.id
  });

  // Manejar cambios en filtros
  const handleFilterChange = useCallback((field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Limpiar filtros
  const handleClearFilters = () => {
    setFilters({
      usuarioId: user?.id || '', // Keep current user as default
      fechaDesde: '',
      fechaHasta: '',
      repartodonaciones: '' // Reset to "both"
    });
  };

  // Funciones de paginación
  const handleChangePage = (groupKey, newPage) => {
    setPaginationState(prev => ({
      ...prev,
      [groupKey]: {
        ...prev[groupKey],
        page: newPage
      }
    }));
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPaginationState({});
  };

  const getPaginatedData = (donaciones, groupKey) => {
    const currentPage = paginationState[groupKey]?.page || 0;
    const startIndex = currentPage * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return donaciones.slice(startIndex, endIndex);
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

  if (loading) {
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
  const totalEventos = reportData.reduce((sum, month) => sum + month.eventos.length, 0);
  const totalDonaciones = reportData.reduce((sum, month) => 
    sum + month.eventos.reduce((eventSum, event) => eventSum + event.donaciones.length, 0), 0
  );

  return (
    <Box>
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
              type="number"
              label="ID de Usuario *"
              value={filters.usuarioId}
              onChange={(e) => handleFilterChange('usuarioId', e.target.value)}
              helperText={canViewAllUsers ? "Ingrese ID del usuario a consultar" : "Solo puedes ver tus propios eventos"}
              disabled={!canViewAllUsers && filters.usuarioId === user?.id?.toString()}
              required
            />
          </Grid>

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
            <FormControl fullWidth>
              <InputLabel>Reparto de Donaciones</InputLabel>
              <Select
                value={filters.repartodonaciones}
                label="Reparto de Donaciones"
                onChange={(e) => handleFilterChange('repartodonaciones', e.target.value)}
              >
                <MenuItem value="">Ambos</MenuItem>
                <MenuItem value="true">Sí</MenuItem>
                <MenuItem value="false">No</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<Search />}
            onClick={() => refetch()}
          >
            Buscar
          </Button>
          <Button
            variant="outlined"
            onClick={handleClearFilters}
          >
            Limpiar Filtros
          </Button>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Filas por página</InputLabel>
            <Select
              value={rowsPerPage}
              label="Filas por página"
              onChange={handleChangeRowsPerPage}
            >
              <MenuItem value={5}>5</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={25}>25</MenuItem>
              <MenuItem value={50}>50</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Resumen general */}
      {reportData.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Assessment />
              Resumen General
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Meses
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
                  {totalEventos}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Donaciones
                </Typography>
                <Typography variant="h4">
                  {totalDonaciones}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Resultados agrupados por mes */}
      {!filters.usuarioId ? (
        <Alert severity="warning">
          Por favor, ingrese un ID de usuario para consultar los eventos. Este campo es obligatorio.
        </Alert>
      ) : reportData.length === 0 ? (
        <Alert severity="info">
          No se encontraron eventos con los filtros aplicados para el usuario {filters.usuarioId}.
        </Alert>
      ) : (
        <Box>
          {reportData.map((monthData, monthIndex) => (
            <Accordion key={monthData.mes} defaultExpanded={monthIndex === 0}>
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
                {monthData.eventos.map((event, eventIndex) => (
                  <Accordion key={`${event.dia}-${eventIndex}`} sx={{ mb: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                        <Typography variant="subtitle1">
                          Día {event.dia}: {event.nombre}
                        </Typography>
                        <Box sx={{ ml: 'auto' }}>
                          <Chip
                            label={`${event.donaciones.length} donaciones`}
                            size="small"
                            color="secondary"
                          />
                        </Box>
                      </Box>
                      {event.descripcion && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          {event.descripcion}
                        </Typography>
                      )}
                    </AccordionSummary>
                    <AccordionDetails>
                      <TableContainer>
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
                            {getPaginatedData(event.donaciones, `${monthData.mes}-${event.dia}`).map((donation, donationIndex) => (
                              <TableRow key={donation.id || `donation-${donationIndex}`}>
                                <TableCell>
                                  <Chip
                                    label={donation.categoria}
                                    size="small"
                                    variant="outlined"
                                  />
                                </TableCell>
                                <TableCell>
                                  {donation.descripcion || '-'}
                                </TableCell>
                                <TableCell align="right">
                                  {formatQuantity(donation.cantidad)}
                                </TableCell>
                                <TableCell>
                                  {formatDate(donation.fechaAlta)}
                                </TableCell>
                                <TableCell>
                                  {donation.usuarioAlta?.nombre || '-'}
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    label={donation.eliminado ? 'Eliminado' : 'Activo'}
                                    color={donation.eliminado ? 'error' : 'success'}
                                    size="small"
                                  />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                      {event.donaciones.length > rowsPerPage && (
                        <TablePagination
                          component="div"
                          count={event.donaciones.length}
                          page={paginationState[`${monthData.mes}-${event.dia}`]?.page || 0}
                          onPageChange={(event, newPage) => handleChangePage(`${monthData.mes}-${event.dia}`, newPage)}
                          rowsPerPage={rowsPerPage}
                          onRowsPerPageChange={handleChangeRowsPerPage}
                          rowsPerPageOptions={[5, 10, 25, 50]}
                          labelRowsPerPage="Filas por página:"
                          labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
                        />
                      )}
                    </AccordionDetails>
                  </Accordion>
                ))}
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default EventReports;