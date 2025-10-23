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
  GetApp,
  ExpandMore,
  FilterList,
  Assessment,
  SwapHoriz,
  Send,
  CallReceived,
  Save,
  BookmarkBorder,
  Delete
} from '@mui/icons-material';
import { useQuery, useMutation } from '@apollo/client';
import { 
  GET_TRANSFER_REPORT,
  GET_SAVED_TRANSFER_FILTERS,
  SAVE_TRANSFER_FILTER,
  UPDATE_TRANSFER_FILTER,
  DELETE_TRANSFER_FILTER
} from '../../graphql/transfers';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { getAuthHeaders } from '../../config/api';

const TRANSFER_TYPES = [
  { value: 'ENVIADA', label: 'Enviadas', icon: <Send />, color: 'primary' },
  { value: 'RECIBIDA', label: 'Recibidas', icon: <CallReceived />, color: 'success' }
];

const TRANSFER_STATUS = [
  { value: 'PENDIENTE', label: 'Pendiente', color: 'warning' },
  { value: 'COMPLETADA', label: 'Completada', color: 'success' },
  { value: 'CANCELADA', label: 'Cancelada', color: 'error' }
];

const TransferReports = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    tipo: '',
    fechaDesde: '',
    fechaHasta: '',
    estado: ''
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState(null);
  
  // Estado para paginación
  const [paginationState, setPaginationState] = useState({});
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Estados para filtros guardados
  const [savedFiltersDialog, setSavedFiltersDialog] = useState(false);
  const [saveFilterDialog, setSaveFilterDialog] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Query para obtener datos de transferencias
  const { data, loading, error, refetch } = useQuery(GET_TRANSFER_REPORT, {
    variables: {
      tipo: filters.tipo || undefined,
      fechaDesde: filters.fechaDesde || undefined,
      fechaHasta: filters.fechaHasta || undefined,
      estado: filters.estado || undefined
    },
    fetchPolicy: 'cache-and-network'
  });

  // Query para obtener filtros guardados
  const { data: savedFiltersData, refetch: refetchSavedFilters } = useQuery(GET_SAVED_TRANSFER_FILTERS, {
    fetchPolicy: 'cache-and-network'
  });

  // Mutations para filtros guardados
  const [saveTransferFilter] = useMutation(SAVE_TRANSFER_FILTER, {
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

  const [deleteTransferFilter] = useMutation(DELETE_TRANSFER_FILTER, {
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
  }, []);

  // Limpiar filtros
  const handleClearFilters = () => {
    setFilters({
      tipo: '',
      fechaDesde: '',
      fechaHasta: '',
      estado: ''
    });
  };

  // Guardar filtro actual
  const handleSaveFilter = () => {
    if (!filterName.trim()) {
      setSnackbar({ open: true, message: 'Por favor ingrese un nombre para el filtro', severity: 'warning' });
      return;
    }

    saveTransferFilter({
      variables: {
        nombre: filterName,
        tipo: filters.tipo || null,
        fechaDesde: filters.fechaDesde || null,
        fechaHasta: filters.fechaHasta || null,
        estado: filters.estado || null
      }
    });
  };

  // Cargar filtro guardado
  const handleLoadFilter = (savedFilter) => {
    const filtros = savedFilter.filtros;
    setFilters({
      tipo: filtros.tipo || '',
      fechaDesde: filtros.fechaDesde || '',
      fechaHasta: filtros.fechaHasta || '',
      estado: filtros.estado || ''
    });
    setSavedFiltersDialog(false);
    setSnackbar({ open: true, message: `Filtro "${savedFilter.nombre}" cargado`, severity: 'success' });
  };

  // Eliminar filtro guardado
  const handleDeleteFilter = (filterId) => {
    deleteTransferFilter({
      variables: { id: filterId }
    });
  };

  // Exportar a Excel
  const handleExportExcel = async () => {
    console.log('[TRANSFER EXCEL EXPORT] Iniciando exportación...');
    console.log('[TRANSFER EXCEL EXPORT] Filtros:', filters);
    
    try {
      setIsExporting(true);
      setExportError(null);

      // Paso 1: Generar el archivo Excel
      console.log('[TRANSFER EXCEL EXPORT] Enviando request para generar archivo...');
      const generateResponse = await axios.post(
        `${process.env.REACT_APP_API_URL}/reports/transfers/excel`,
        {
          tipo: filters.tipo || null,
          fecha_desde: filters.fechaDesde || null,
          fecha_hasta: filters.fechaHasta || null,
          estado: filters.estado || null
        },
        {
          headers: getAuthHeaders(),
          timeout: 30000
        }
      );
      
      console.log('[TRANSFER EXCEL EXPORT] Respuesta de generación:', generateResponse.data);

      const { file_id, filename } = generateResponse.data;
      console.log('[TRANSFER EXCEL EXPORT] File ID:', file_id, 'Filename:', filename);

      // Paso 2: Descargar el archivo generado
      console.log('[TRANSFER EXCEL EXPORT] Descargando archivo...');
      const downloadResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/reports/downloads/${file_id}`,
        {
          headers: getAuthHeaders(),
          responseType: 'blob',
          timeout: 30000
        }
      );
      
      console.log('[TRANSFER EXCEL EXPORT] Archivo descargado, tamaño:', downloadResponse.data.size);

      // Crear enlace de descarga
      console.log('[TRANSFER EXCEL EXPORT] Creando enlace de descarga...');
      const url = window.URL.createObjectURL(new Blob([downloadResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      console.log('[TRANSFER EXCEL EXPORT] ¡Descarga completada!');
    } catch (error) {
      console.error('[TRANSFER EXCEL EXPORT] Error al exportar Excel:', error);
      if (error.response) {
        console.error('[TRANSFER EXCEL EXPORT] Response data:', error.response.data);
        console.error('[TRANSFER EXCEL EXPORT] Response status:', error.response.status);
        console.error('[TRANSFER EXCEL EXPORT] Response headers:', error.response.headers);
      }
      setExportError('Error al generar el archivo Excel. Por favor, intente nuevamente.');
    } finally {
      setIsExporting(false);
      console.log('[TRANSFER EXCEL EXPORT] Proceso finalizado');
    }
  };

  // Formatear fecha para mostrar
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Formatear cantidad
  const formatQuantity = (quantity) => {
    return new Intl.NumberFormat('es-ES').format(quantity);
  };

  // Obtener color del tipo de transferencia
  const getTransferTypeInfo = (tipo) => {
    return TRANSFER_TYPES.find(t => t.value === tipo) || { label: tipo, color: 'default', icon: <SwapHoriz /> };
  };

  // Obtener color del estado
  const getStatusInfo = (estado) => {
    return TRANSFER_STATUS.find(s => s.value === estado) || { label: estado, color: 'default' };
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

  const getPaginatedData = (transferencias, groupKey) => {
    const currentPage = paginationState[groupKey]?.page || 0;
    const startIndex = currentPage * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return transferencias.slice(startIndex, endIndex);
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

  const reportData = data?.transferReport || [];
  const totalTransferencias = reportData.reduce((sum, group) => sum + group.totalTransferencias, 0);
  const totalItems = reportData.reduce((sum, group) => sum + group.totalItems, 0);

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
            <FormControl fullWidth>
              <InputLabel>Tipo de Transferencia</InputLabel>
              <Select
                value={filters.tipo}
                label="Tipo de Transferencia"
                onChange={(e) => handleFilterChange('tipo', e.target.value)}
              >
                <MenuItem value="">Todos los tipos</MenuItem>
                {TRANSFER_TYPES.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {type.icon}
                      {type.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
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
              <InputLabel>Estado</InputLabel>
              <Select
                value={filters.estado}
                label="Estado"
                onChange={(e) => handleFilterChange('estado', e.target.value)}
              >
                <MenuItem value="">Todos los estados</MenuItem>
                {TRANSFER_STATUS.map(status => (
                  <MenuItem key={status.value} value={status.value}>
                    {status.label}
                  </MenuItem>
                ))}
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
          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={() => setSaveFilterDialog(true)}
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
          <Button
            variant="contained"
            color="success"
            startIcon={isExporting ? <CircularProgress size={20} /> : <GetApp />}
            onClick={handleExportExcel}
            disabled={isExporting || reportData.length === 0}
          >
            {isExporting ? 'Exportando...' : 'Exportar Excel'}
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

        {exportError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {exportError}
          </Alert>
        )}
      </Paper>

      {/* Resumen general */}
      {reportData.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Assessment />
              Resumen de Transferencias
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Organizaciones
                </Typography>
                <Typography variant="h4">
                  {reportData.length}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Transferencias
                </Typography>
                <Typography variant="h4">
                  {formatQuantity(totalTransferencias)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Unidades
                </Typography>
                <Typography variant="h4">
                  {formatQuantity(totalItems)}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Resultados agrupados */}
      {reportData.length === 0 ? (
        <Alert severity="info">
          No se encontraron transferencias con los filtros aplicados.
        </Alert>
      ) : (
        <Box>
          {reportData.map((group, index) => {
            const typeInfo = getTransferTypeInfo(group.tipo);
            const groupKey = `${group.organizacion}-${group.tipo}`;
            
            return (
              <Accordion key={groupKey} defaultExpanded={index === 0}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {typeInfo.icon}
                      <Typography variant="h6">
                        {group.organizacion}
                      </Typography>
                    </Box>
                    <Chip
                      label={typeInfo.label}
                      color={typeInfo.color}
                      size="small"
                    />
                    <Box sx={{ ml: 'auto', display: 'flex', gap: 2 }}>
                      <Chip
                        label={`${group.totalTransferencias} transferencias`}
                        variant="outlined"
                        size="small"
                      />
                      <Chip
                        label={`${formatQuantity(group.totalItems)} unidades`}
                        color="primary"
                        size="small"
                      />
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Fecha</TableCell>
                          <TableCell>Tipo</TableCell>
                          <TableCell>Organización</TableCell>
                          <TableCell align="right">Cantidad</TableCell>
                          <TableCell>Items</TableCell>
                          <TableCell>Estado</TableCell>
                          <TableCell>Notas</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {getPaginatedData(group.transferencias, groupKey).map((transfer) => {
                          const transferTypeInfo = getTransferTypeInfo(transfer.tipo);
                          const statusInfo = getStatusInfo(transfer.estado);
                          
                          return (
                            <TableRow key={transfer.id}>
                              <TableCell>
                                {formatDate(transfer.fechaTransferencia)}
                              </TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  {transferTypeInfo.icon}
                                  <Chip
                                    label={transferTypeInfo.label}
                                    color={transferTypeInfo.color}
                                    size="small"
                                  />
                                </Box>
                              </TableCell>
                              <TableCell>
                                {transfer.organizacionContraparte}
                              </TableCell>
                              <TableCell align="right">
                                {formatQuantity(transfer.totalQuantity || transfer.totalItems)}
                              </TableCell>
                              <TableCell>
                                {transfer.donaciones && transfer.donaciones.length > 0 ? (
                                  <Box>
                                    {transfer.donaciones.map((item, idx) => (
                                      <Chip
                                        key={idx}
                                        label={`${item.categoria}: ${item.descripcion} (${item.cantidad})`}
                                        size="small"
                                        variant="outlined"
                                        sx={{ mr: 0.5, mb: 0.5 }}
                                      />
                                    ))}
                                  </Box>
                                ) : (
                                  `${transfer.totalItems} items`
                                )}
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={statusInfo.label}
                                  color={statusInfo.color}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                {transfer.notas || '-'}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  <TablePagination
                    component="div"
                    count={group.transferencias.length}
                    page={paginationState[groupKey]?.page || 0}
                    onPageChange={(event, newPage) => handleChangePage(groupKey, newPage)}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    rowsPerPageOptions={[5, 10, 25, 50]}
                    labelRowsPerPage="Filas por página:"
                    labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
                  />
                </AccordionDetails>
              </Accordion>
            );
          })}
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
          {savedFiltersData?.savedTransferFilters?.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2 }}>
              No tienes filtros guardados aún.
            </Typography>
          ) : (
            <List>
              {savedFiltersData?.savedTransferFilters?.map((filter) => (
                <ListItem key={filter.id} divider>
                  <ListItemText
                    primary={filter.nombre}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Tipo: {filter.filtros.tipo || 'Todos'} | 
                          Estado: {filter.filtros.estado || 'Todos'} | 
                          Fechas: {filter.filtros.fechaDesde || 'Sin límite'} - {filter.filtros.fechaHasta || 'Sin límite'}
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

export default TransferReports;