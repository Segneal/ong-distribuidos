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
  Divider,
  TablePagination
} from '@mui/material';
import {
  Search,
  GetApp,
  ExpandMore,
  FilterList,
  Assessment
} from '@mui/icons-material';
import { useQuery } from '@apollo/client';
import { GET_DONATION_REPORT } from '../../graphql/donations';
import { useAuth } from '../../contexts/AuthContext';
import DonationFilters from './DonationFilters';
import axios from 'axios';
import { getAuthHeaders } from '../../config/api';

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

const DonationReports = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState({
    categoria: '',
    fechaDesde: '',
    fechaHasta: '',
    eliminado: null
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState(null);
  
  // Estado para paginación
  const [paginationState, setPaginationState] = useState({});
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Query para obtener datos de donaciones
  const { data, loading, error, refetch } = useQuery(GET_DONATION_REPORT, {
    variables: {
      categoria: filters.categoria || undefined,
      fechaDesde: filters.fechaDesde || undefined,
      fechaHasta: filters.fechaHasta || undefined,
      eliminado: filters.eliminado
    },
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
      categoria: '',
      fechaDesde: '',
      fechaHasta: '',
      eliminado: null
    });
  };

  // Exportar a Excel
  const handleExportExcel = async () => {
    console.log('[EXCEL EXPORT] Iniciando exportación...');
    console.log('[EXCEL EXPORT] Filtros:', filters);
    console.log('[EXCEL EXPORT] URL:', `${process.env.REACT_APP_API_URL}/reports/donations/excel`);
    console.log('[EXCEL EXPORT] Headers:', getAuthHeaders());
    
    try {
      setIsExporting(true);
      setExportError(null);

      // Paso 1: Generar el archivo Excel
      console.log('[EXCEL EXPORT] Enviando request para generar archivo...');
      const generateResponse = await axios.post(
        `${process.env.REACT_APP_API_URL}/reports/donations/excel`,
        {
          categoria: filters.categoria || null,
          fecha_desde: filters.fechaDesde || null,
          fecha_hasta: filters.fechaHasta || null,
          eliminado: filters.eliminado
        },
        {
          headers: getAuthHeaders(),
          timeout: 30000 // 30 segundos timeout
        }
      );
      
      console.log('[EXCEL EXPORT] Respuesta de generación:', generateResponse.data);

      const { file_id, filename } = generateResponse.data;
      console.log('[EXCEL EXPORT] File ID:', file_id, 'Filename:', filename);

      // Paso 2: Descargar el archivo generado
      console.log('[EXCEL EXPORT] Descargando archivo...');
      const downloadResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/reports/downloads/${file_id}`,
        {
          headers: getAuthHeaders(),
          responseType: 'blob',
          timeout: 30000 // 30 segundos timeout
        }
      );
      
      console.log('[EXCEL EXPORT] Archivo descargado, tamaño:', downloadResponse.data.size);

      // Crear enlace de descarga
      console.log('[EXCEL EXPORT] Creando enlace de descarga...');
      const url = window.URL.createObjectURL(new Blob([downloadResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      console.log('[EXCEL EXPORT] ¡Descarga completada!');
    } catch (error) {
      console.error('[EXCEL EXPORT] Error al exportar Excel:', error);
      if (error.response) {
        console.error('[EXCEL EXPORT] Response data:', error.response.data);
        console.error('[EXCEL EXPORT] Response status:', error.response.status);
        console.error('[EXCEL EXPORT] Response headers:', error.response.headers);
      }
      setExportError('Error al generar el archivo Excel. Por favor, intente nuevamente.');
    } finally {
      setIsExporting(false);
      console.log('[EXCEL EXPORT] Proceso finalizado');
    }
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
    // Reset all pages to 0 when changing rows per page
    setPaginationState({});
  };

  const getPaginatedData = (registros, groupKey) => {
    const currentPage = paginationState[groupKey]?.page || 0;
    const startIndex = currentPage * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return registros.slice(startIndex, endIndex);
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

  const reportData = data?.donationReport || [];
  const totalGeneral = reportData.reduce((sum, group) => sum + group.totalCantidad, 0);
  
  console.log('[DONATION REPORTS] Report data:', reportData);
  console.log('[DONATION REPORTS] Report data length:', reportData.length);
  console.log('[DONATION REPORTS] Is exporting:', isExporting);
  console.log('[DONATION REPORTS] Button disabled:', isExporting || reportData.length === 0);

  return (
    <Box>
      {/* Filtros guardados */}
      <DonationFilters
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
            <FormControl fullWidth>
              <InputLabel>Categoría</InputLabel>
              <Select
                value={filters.categoria}
                label="Categoría"
                onChange={(e) => handleFilterChange('categoria', e.target.value)}
              >
                <MenuItem value="">Todas las categorías</MenuItem>
                {DONATION_CATEGORIES.map(category => (
                  <MenuItem key={category} value={category}>
                    {category}
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
                value={filters.eliminado === null ? '' : (filters.eliminado ? 'true' : 'false')}
                label="Estado"
                onChange={(e) => {
                  const value = e.target.value;
                  handleFilterChange('eliminado', value === '' ? null : value === 'true');
                }}
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="false">Activos</MenuItem>
                <MenuItem value="true">Eliminados</MenuItem>
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
              Resumen General
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Categorías
                </Typography>
                <Typography variant="h4">
                  {reportData.length}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total de Registros
                </Typography>
                <Typography variant="h4">
                  {reportData.reduce((sum, group) => sum + group.registros.length, 0)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Cantidad Total
                </Typography>
                <Typography variant="h4">
                  {formatQuantity(totalGeneral)}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Resultados agrupados */}
      {reportData.length === 0 ? (
        <Alert severity="info">
          No se encontraron donaciones con los filtros aplicados.
        </Alert>
      ) : (
        <Box>
          {reportData.map((group, index) => (
            <Accordion key={`${group.categoria}-${group.eliminado}`} defaultExpanded={index === 0}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <Typography variant="h6">
                    {group.categoria}
                  </Typography>
                  <Chip
                    label={group.eliminado ? 'Eliminados' : 'Activos'}
                    color={group.eliminado ? 'error' : 'success'}
                    size="small"
                  />
                  <Box sx={{ ml: 'auto', display: 'flex', gap: 2 }}>
                    <Chip
                      label={`${group.registros.length} registros`}
                      variant="outlined"
                      size="small"
                    />
                    <Chip
                      label={`Total: ${formatQuantity(group.totalCantidad)}`}
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
                      <TableRow key="header">
                        <TableCell>Fecha Alta</TableCell>
                        <TableCell>Descripción</TableCell>
                        <TableCell align="right">Cantidad</TableCell>
                        <TableCell>Usuario Alta</TableCell>
                        <TableCell>Fecha Modificación</TableCell>
                        <TableCell>Usuario Modificación</TableCell>
                        <TableCell>Estado</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {getPaginatedData(group.registros, `${group.categoria}-${group.eliminado}`).map((donation, index) => (
                        <TableRow key={donation.id || `donation-${index}`}>
                          <TableCell>
                            {formatDate(donation.fechaAlta)}
                          </TableCell>
                          <TableCell>
                            {donation.descripcion || '-'}
                          </TableCell>
                          <TableCell align="right">
                            {formatQuantity(donation.cantidad)}
                          </TableCell>
                          <TableCell>
                            {donation.usuarioAlta?.nombre || '-'}
                          </TableCell>
                          <TableCell>
                            {formatDate(donation.fechaModificacion)}
                          </TableCell>
                          <TableCell>
                            {donation.usuarioModificacion?.nombre || '-'}
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
                <TablePagination
                  component="div"
                  count={group.registros.length}
                  page={paginationState[`${group.categoria}-${group.eliminado}`]?.page || 0}
                  onPageChange={(event, newPage) => handleChangePage(`${group.categoria}-${group.eliminado}`, newPage)}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                  labelRowsPerPage="Filas por página:"
                  labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
                />
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default DonationReports;