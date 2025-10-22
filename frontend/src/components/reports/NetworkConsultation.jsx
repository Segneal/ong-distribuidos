import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  InputAdornment
} from '@mui/material';
import {
  Search,
  Business,
  Person,
  NetworkCheck,
  Warning,
  Info
} from '@mui/icons-material';
import axios from 'axios';
import { getAuthHeaders, API_ENDPOINTS } from '../../config/api';
import { useAuth } from '../../contexts/AuthContext';

const NetworkConsultation = () => {
  const { user } = useAuth();
  const [organizationIds, setOrganizationIds] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Verificar que el usuario sea Presidente
  const isPresident = user?.role === 'PRESIDENTE';

  // Manejar consulta SOAP
  const handleConsultation = async () => {
    if (!organizationIds.trim()) {
      setError('Debe ingresar al menos un ID de organización');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResults(null);

      // Convertir string de IDs a array de números
      const idsArray = organizationIds
        .split(',')
        .map(id => id.trim())
        .filter(id => id !== '')
        .map(id => parseInt(id, 10))
        .filter(id => !isNaN(id));

      if (idsArray.length === 0) {
        setError('Debe ingresar IDs de organización válidos (números separados por comas)');
        return;
      }

      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}${API_ENDPOINTS.NETWORK.CONSULTATION}`,
        { organizationIds: idsArray },
        { headers: getAuthHeaders() }
      );

      setResults(response.data);
    } catch (error) {
      console.error('Error en consulta SOAP:', error);
      
      if (error.response?.status === 403) {
        setError('No tiene permisos para realizar consultas de red. Solo los Presidentes pueden acceder a esta funcionalidad.');
      } else if (error.response?.status === 400) {
        setError(error.response.data?.error || 'Datos de entrada inválidos');
      } else if (error.response?.status === 500) {
        setError('Error del servicio SOAP. El servicio externo no está disponible o hay un problema de conectividad.');
      } else {
        setError('Error al realizar la consulta. Por favor, intente nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Limpiar formulario
  const handleClear = () => {
    setOrganizationIds('');
    setResults(null);
    setError(null);
  };

  // Verificar acceso
  if (!isPresident) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Warning />
            <Typography variant="body1">
              Acceso Restringido - Solo los Presidentes pueden realizar consultas de red SOAP
            </Typography>
          </Box>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Información sobre la funcionalidad */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Info />
          <Typography variant="body2">
            Esta funcionalidad permite consultar información de presidentes y organizaciones 
            de la red externa de ONGs mediante integración SOAP.
          </Typography>
        </Box>
      </Alert>

      {/* Formulario de consulta */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <NetworkCheck />
          Consulta de Red SOAP
        </Typography>
        
        <Grid container spacing={3} alignItems="end">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="IDs de Organizaciones"
              placeholder="Ej: 1, 2, 3, 4"
              value={organizationIds}
              onChange={(e) => setOrganizationIds(e.target.value)}
              helperText="Ingrese los IDs de las organizaciones separados por comas"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Business />
                  </InputAdornment>
                ),
              }}
              disabled={loading}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <Search />}
                onClick={handleConsultation}
                disabled={loading || !organizationIds.trim()}
                fullWidth
              >
                {loading ? 'Consultando...' : 'Consultar'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleClear}
                disabled={loading}
              >
                Limpiar
              </Button>
            </Box>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {/* Resultados */}
      {results && (
        <Box>
          {/* Resumen de resultados */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <NetworkCheck />
                Resumen de Consulta
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">
                    Organizaciones Consultadas
                  </Typography>
                  <Typography variant="h4">
                    {results.organizations?.length || 0}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">
                    Presidentes Encontrados
                  </Typography>
                  <Typography variant="h4">
                    {results.presidents?.length || 0}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">
                    Estado de Consulta
                  </Typography>
                  <Chip 
                    label="Exitosa"
                    color="success"
                    size="small"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Datos de Presidentes */}
          {results.presidents && results.presidents.length > 0 && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Person />
                Información de Presidentes
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID Organización</TableCell>
                      <TableCell>Nombre</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Teléfono</TableCell>
                      <TableCell>Fecha Inicio</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.presidents.map((president, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip 
                            label={president.organizationId || '-'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{president.nombre || '-'}</TableCell>
                        <TableCell>{president.email || '-'}</TableCell>
                        <TableCell>{president.telefono || '-'}</TableCell>
                        <TableCell>
                          {president.fechaInicio ? 
                            new Date(president.fechaInicio).toLocaleDateString('es-ES') : '-'
                          }
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}

          {/* Datos de Organizaciones */}
          {results.organizations && results.organizations.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Business />
                Información de Organizaciones
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Nombre</TableCell>
                      <TableCell>Descripción</TableCell>
                      <TableCell>Dirección</TableCell>
                      <TableCell>Teléfono</TableCell>
                      <TableCell>Estado</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.organizations.map((organization, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip 
                            label={organization.id || '-'}
                            size="small"
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {organization.nombre || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {organization.descripcion || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>{organization.direccion || '-'}</TableCell>
                        <TableCell>{organization.telefono || '-'}</TableCell>
                        <TableCell>
                          <Chip 
                            label={organization.activa ? 'Activa' : 'Inactiva'}
                            color={organization.activa ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}

          {/* Mensaje si no hay resultados */}
          {(!results.presidents || results.presidents.length === 0) && 
           (!results.organizations || results.organizations.length === 0) && (
            <Alert severity="info">
              No se encontraron datos para los IDs de organización consultados.
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );
};

export default NetworkConsultation;