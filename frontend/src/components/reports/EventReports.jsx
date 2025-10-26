import React, { useState, useCallback, useEffect } from 'react';
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
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Snackbar
} from '@mui/material';
import {
  Search,
  ExpandMore,
  FilterList,
  Assessment,
  Event,
  Save,
  BookmarkBorder,
  Delete,
  Edit,
  People,
  PersonAdd,
  CalendarToday,
  Inventory,
  TrendingUp,
  Groups,
  EventAvailable
} from '@mui/icons-material';
import { useQuery, useMutation } from '@apollo/client';
import { 
  GET_EVENT_PARTICIPATION_REPORT,
  GET_SAVED_EVENT_FILTERS,
  SAVE_EVENT_FILTER,
  UPDATE_EVENT_FILTER,
  DELETE_EVENT_FILTER
  // GET_ORGANIZATION_USERS  // Temporarily disabled
} from '../../graphql/events';
import { useAuth } from '../../contexts/AuthContext';

const EventReports = () => {
  const { user } = useAuth();
  
  // Check if user can see other users' reports
  const canViewAllUsers = user?.role === 'PRESIDENTE' || user?.role === 'COORDINADOR';
  
  const [filters, setFilters] = useState({
    usuarioId: canViewAllUsers ? '0' : (user?.id?.toString() || ''), // Default to "All users" for PRESIDENTE/COORDINADOR
    fechaDesde: '',
    fechaHasta: '',
    repartodonaciones: '' // '' = both, 'true' = yes, 'false' = no
  });
  
  // Estado para paginación
  const [paginationState, setPaginationState] = useState({});
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Estados para filtros guardados
  const [savedFiltersDialog, setSavedFiltersDialog] = useState(false);
  const [saveFilterDialog, setSaveFilterDialog] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [userNotFoundError, setUserNotFoundError] = useState(false);

  // Query para obtener datos de eventos
  const { data, loading, error, refetch } = useQuery(GET_EVENT_PARTICIPATION_REPORT, {
    variables: {
      usuarioId: filters.usuarioId ? parseInt(filters.usuarioId) : user?.id,
      fechaDesde: filters.fechaDesde || undefined,
      fechaHasta: filters.fechaHasta || undefined,
      repartodonaciones: filters.repartodonaciones === '' ? undefined : filters.repartodonaciones === 'true'
    },
    fetchPolicy: 'cache-and-network',
    skip: (!filters.usuarioId || filters.usuarioId === '') && !user?.id,
    onError: (error) => {
      if (error.message.includes('User with ID') && error.message.includes('not found')) {
        setUserNotFoundError(true);
      }
    }
  });

  // Query para obtener filtros guardados
  const { data: savedFiltersData, refetch: refetchSavedFilters } = useQuery(GET_SAVED_EVENT_FILTERS, {
    fetchPolicy: 'cache-and-network'
  });

  // Query para obtener usuarios de la organización (solo para PRESIDENTE/COORDINADOR)
  // Temporarily disabled due to resolver issues
  // const { data: usersData } = useQuery(GET_ORGANIZATION_USERS, {
  //   skip: !canViewAllUsers,
  //   fetchPolicy: 'cache-and-network'
  // });

  // Mutations para filtros guardados
  const [saveEventFilter] = useMutation(SAVE_EVENT_FILTER, {
    onCompleted: () => {
      setSnackbar({ open: true, message: 'Filtro guardado exitosamente', severity: 'success' });
      setSaveFilterDialog(false);
      setFilterName('');
      refetchSavedFilters();
    },
    onError: (error) => {
      setSnackbar({ open: true, message: `Error al guardar filtro: ${error.message}`, severity: 'error' });
    }
  });

  const [deleteEventFilter] = useMutation(DELETE_EVENT_FILTER, {
    onCompleted: () => {
      setSnackbar({ open: true, message: 'Filtro eliminado exitosamente', severity: 'success' });
      refetchSavedFilters();
    },
    onError: (error) => {
      setSnackbar({ open: true, message: `Error al eliminar filtro: ${error.message}`, severity: 'error' });
    }
  });

  // Manejar cambios en filtros
  const handleFilterChange = useCallback((field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpiar error de usuario no encontrado cuando se cambia el ID
    if (field === 'usuarioId') {
      setUserNotFoundError(false);
    }
  }, []);

  // Limpiar filtros
  const handleClearFilters = () => {
    setFilters({
      usuarioId: canViewAllUsers ? '0' : (user?.id?.toString() || ''), // Default to "All users" for PRESIDENTE/COORDINADOR
      fechaDesde: '',
      fechaHasta: '',
      repartodonaciones: '' // Reset to "both"
    });
    setUserNotFoundError(false);
  };

  // Guardar filtro actual
  const handleSaveFilter = () => {
    if (!filterName.trim()) {
      setSnackbar({ open: true, message: 'Por favor ingrese un nombre para el filtro', severity: 'warning' });
      return;
    }

    saveEventFilter({
      variables: {
        nombre: filterName,
        usuarioId: filters.usuarioId ? parseInt(filters.usuarioId) : null,
        fechaDesde: filters.fechaDesde || null,
        fechaHasta: filters.fechaHasta || null,
        repartodonaciones: filters.repartodonaciones === '' ? null : filters.repartodonaciones === 'true'
      }
    });
  };

  // Cargar filtro guardado
  const handleLoadFilter = (savedFilter) => {
    const filtros = savedFilter.filtros;
    setFilters({
      usuarioId: filtros.usuarioId?.toString() || user?.id?.toString() || '',
      fechaDesde: filtros.fechaDesde || '',
      fechaHasta: filtros.fechaHasta || '',
      repartodonaciones: filtros.repartodonaciones === null ? '' : filtros.repartodonaciones.toString()
    });
    setSavedFiltersDialog(false);
    setUserNotFoundError(false);
    setSnackbar({ open: true, message: `Filtro "${savedFilter.nombre}" cargado`, severity: 'success' });
  };

  // Eliminar filtro guardado
  const handleDeleteFilter = (filterId) => {
    deleteEventFilter({
      variables: { id: filterId }
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

  if (error && !userNotFoundError) {
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
  
  // Calcular participantes únicos
  const participantesUnicos = new Set();
  reportData.forEach(month => {
    month.eventos.forEach(event => {
      if (event.participantes) {
        event.participantes.forEach(participant => {
          participantesUnicos.add(participant.id);
        });
      }
    });
  });
  const totalParticipantesUnicos = participantesUnicos.size;

  return (
    <Box>
      {/* Formulario de filtros */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterList />
          Filtros de Búsqueda
        </Typography>

        <Grid container spacing={3}>
          {canViewAllUsers && (
            <Grid item xs={12} md={3}>
              <FormControl fullWidth error={userNotFoundError}>
                <InputLabel>Usuario *</InputLabel>
                <Select
                  value={filters.usuarioId}
                  label="Usuario *"
                  onChange={(e) => handleFilterChange('usuarioId', e.target.value)}
                  required
                >
                  <MenuItem value="0">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Assessment />
                      <strong>Todos los usuarios de la organización</strong>
                    </Box>
                  </MenuItem>
                  <MenuItem value="11">Admin (PRESIDENTE) - ID: 11</MenuItem>
                  <MenuItem value="13">Carlos López (COORDINADOR) - ID: 13</MenuItem>
                  <MenuItem value="14">AnaSAT Martínez (VOLUNTARIO) - ID: 14</MenuItem>
                  <MenuItem value="15">Pedro Rodríguez (VOLUNTARIO) - ID: 15</MenuItem>
                </Select>
                {userNotFoundError && (
                  <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
                    Usuario con ID {filters.usuarioId} no encontrado
                  </Typography>
                )}
              </FormControl>
            </Grid>
          )}

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
            disabled={userNotFoundError}
          >
            Buscar
          </Button>
          <Button
            variant="outlined"
            onClick={handleClearFilters}
          >
            Limpiar Filtros
          </Button>
          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={() => setSaveFilterDialog(true)}
            disabled={!filters.usuarioId || userNotFoundError}
          >
            Guardar Filtro
          </Button>
          <Button
            variant="outlined"
            startIcon={<BookmarkBorder />}
            onClick={() => setSavedFiltersDialog(true)}
          >
            Filtros Guardados
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
              Resumen General - {filters.usuarioId === '0' ? 'Todos los usuarios' : `Usuario ${filters.usuarioId}`}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Total de Meses
                </Typography>
                <Typography variant="h4">
                  {reportData.length}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Total de Eventos
                </Typography>
                <Typography variant="h4">
                  {totalEventos}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Participantes Únicos
                </Typography>
                <Typography variant="h4">
                  {totalParticipantesUnicos}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
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
      {userNotFoundError ? (
        <Alert severity="error">
          No se encontró un usuario con ID {filters.usuarioId}. Por favor, verifique el ID e intente nuevamente.
        </Alert>
      ) : !filters.usuarioId ? (
        <Alert severity="warning">
          {canViewAllUsers 
            ? "Por favor, seleccione un usuario para consultar los eventos. Este campo es obligatorio."
            : "Consultando eventos del usuario actual..."
          }
        </Alert>
      ) : reportData.length === 0 && !loading ? (
        <Alert severity="info">
          No se encontraron eventos con los filtros aplicados para {filters.usuarioId === '0' ? 'todos los usuarios de la organización' : `el usuario ${filters.usuarioId}`}.
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
                        <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
                          <Chip
                            label={`${event.participantes?.length || 0} participantes`}
                            size="small"
                            color="primary"
                          />
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
                    <AccordionDetails sx={{ p: 3 }}>
                      {/* Información de participantes */}
                      {event.participantes && event.participantes.length > 0 && (
                        <Card sx={{ mb: 3, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
                          <CardContent sx={{ pb: '16px !important' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                              <Groups color="primary" />
                              <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
                                Participantes
                              </Typography>
                              <Chip 
                                label={event.participantes.length} 
                                size="small" 
                                color="primary"
                                sx={{ ml: 1 }}
                              />
                            </Box>
                            <Grid container spacing={1}>
                              {event.participantes.map((participant, idx) => (
                                <Grid item xs={12} sm={6} md={4} key={idx}>
                                  <Card sx={{ 
                                    backgroundColor: 'white',
                                    border: '1px solid #e2e8f0',
                                    '&:hover': {
                                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                      transform: 'translateY(-1px)',
                                      transition: 'all 0.2s ease-in-out'
                                    }
                                  }}>
                                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <PersonAdd sx={{ fontSize: 20, color: '#64748b' }} />
                                        <Box>
                                          <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
                                            {participant.nombre} {participant.apellido}
                                          </Typography>
                                          <Chip 
                                            label={participant.rol} 
                                            size="small" 
                                            variant="outlined"
                                            color={
                                              participant.rol === 'PRESIDENTE' ? 'error' :
                                              participant.rol === 'COORDINADOR' ? 'warning' :
                                              'default'
                                            }
                                            sx={{ mt: 0.5, fontSize: '0.7rem' }}
                                          />
                                        </Box>
                                      </Box>
                                    </CardContent>
                                  </Card>
                                </Grid>
                              ))}
                            </Grid>
                          </CardContent>
                        </Card>
                      )}

                      {/* Sección de donaciones */}
                      <Card sx={{ backgroundColor: 'white', border: '1px solid #e2e8f0' }}>
                        <CardContent sx={{ pb: '16px !important' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <Inventory color="secondary" />
                            <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
                              Donaciones Distribuidas
                            </Typography>
                            <Chip 
                              label={event.donaciones.length} 
                              size="small" 
                              color="secondary"
                              sx={{ ml: 1 }}
                            />
                          </Box>

                          {event.donaciones.length > 0 ? (
                            <TableContainer sx={{ borderRadius: 2, border: '1px solid #e2e8f0' }}>
                              <Table size="small">
                                <TableHead>
                                  <TableRow sx={{ backgroundColor: '#f1f5f9' }}>
                                    <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Categoría</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Descripción</TableCell>
                                    <TableCell align="right" sx={{ fontWeight: 'bold', color: '#374151' }}>Cantidad</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Fecha Alta</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Usuario Alta</TableCell>
                                    <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Estado</TableCell>
                                  </TableRow>
                                </TableHead>
                                <TableBody>
                                  {getPaginatedData(event.donaciones, `${monthData.mes}-${event.dia}`).map((donation, donationIndex) => (
                                    <TableRow 
                                      key={donation.id || `donation-${donationIndex}`}
                                      sx={{ 
                                        '&:hover': { backgroundColor: '#f8fafc' },
                                        '&:nth-of-type(even)': { backgroundColor: '#fafbfc' }
                                      }}
                                    >
                                      <TableCell>
                                        <Chip
                                          label={donation.categoria}
                                          size="small"
                                          variant="outlined"
                                          color="primary"
                                          sx={{ fontWeight: 'medium' }}
                                        />
                                      </TableCell>
                                      <TableCell sx={{ maxWidth: 200 }}>
                                        <Typography variant="body2" sx={{ 
                                          overflow: 'hidden',
                                          textOverflow: 'ellipsis',
                                          whiteSpace: 'nowrap'
                                        }}>
                                          {donation.descripcion || '-'}
                                        </Typography>
                                      </TableCell>
                                      <TableCell align="right">
                                        <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#059669' }}>
                                          {formatQuantity(donation.cantidad)}
                                        </Typography>
                                      </TableCell>
                                      <TableCell>
                                        <Typography variant="body2" color="text.secondary">
                                          {formatDate(donation.fechaAlta)}
                                        </Typography>
                                      </TableCell>
                                      <TableCell>
                                        <Typography variant="body2">
                                          {donation.usuarioAlta?.nombre || '-'}
                                        </Typography>
                                      </TableCell>
                                      <TableCell>
                                        <Chip
                                          label={donation.eliminado ? 'Eliminado' : 'Activo'}
                                          color={donation.eliminado ? 'error' : 'success'}
                                          size="small"
                                          variant="outlined"
                                        />
                                      </TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </TableContainer>
                          ) : (
                            <Box sx={{ 
                              textAlign: 'center', 
                              py: 4, 
                              backgroundColor: '#f8fafc',
                              borderRadius: 2,
                              border: '1px dashed #cbd5e1'
                            }}>
                              <Inventory sx={{ fontSize: 48, color: '#94a3b8', mb: 1 }} />
                              <Typography variant="body1" color="text.secondary">
                                No se distribuyeron donaciones en este evento
                              </Typography>
                            </Box>
                          )}
                          {event.donaciones.length > rowsPerPage && (
                            <Box sx={{ mt: 2 }}>
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
                                sx={{
                                  borderTop: '1px solid #e2e8f0',
                                  backgroundColor: '#f8fafc'
                                }}
                              />
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}

      {/* Diálogo para guardar filtro */}
      <Dialog open={saveFilterDialog} onClose={() => setSaveFilterDialog(false)} maxWidth="sm" fullWidth>
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
            helperText="Ingrese un nombre descriptivo para este filtro"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveFilterDialog(false)}>Cancelar</Button>
          <Button onClick={handleSaveFilter} variant="contained">Guardar</Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo para filtros guardados */}
      <Dialog open={savedFiltersDialog} onClose={() => setSavedFiltersDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Filtros Guardados</DialogTitle>
        <DialogContent>
          {savedFiltersData?.savedEventFilters?.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2 }}>
              No tienes filtros guardados aún.
            </Typography>
          ) : (
            <List>
              {savedFiltersData?.savedEventFilters?.map((filter) => (
                <ListItem key={filter.id} divider>
                  <ListItemText
                    primary={filter.nombre}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Usuario: {filter.filtros.usuarioId || 'Actual'} | 
                          Fechas: {filter.filtros.fechaDesde || 'Sin límite'} - {filter.filtros.fechaHasta || 'Sin límite'} | 
                          Donaciones: {filter.filtros.repartodonaciones === null ? 'Ambos' : filter.filtros.repartodonaciones ? 'Sí' : 'No'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Creado: {new Date(filter.fechaCreacion).toLocaleDateString('es-ES')}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Button
                      size="small"
                      onClick={() => handleLoadFilter(filter)}
                      sx={{ mr: 1 }}
                    >
                      Cargar
                    </Button>
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteFilter(filter.id)}
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSavedFiltersDialog(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar para notificaciones */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EventReports;