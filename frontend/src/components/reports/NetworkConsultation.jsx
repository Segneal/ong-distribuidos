import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Business as BusinessIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../../hooks/useAuth';

const NetworkConsultation = () => {
  const { user } = useAuth();
  const [organizationIds, setOrganizationIds] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [expandedOrg, setExpandedOrg] = useState(false);

  // Check if user has permission (only Presidentes)
  const hasPermission = user && user.rol === 'Presidente';

  const handleConsultation = async () => {
    if (!organizationIds.trim()) {
      setError('Debes ingresar al menos un ID de organización');
      return;
    }

    // Parse and validate IDs
    const ids = organizationIds
      .split(',')
      .map(id => id.trim())
      .filter(id => id !== '')
      .map(id => parseInt(id))
      .filter(id => !isNaN(id));

    if (ids.length === 0) {
      setError('Debes ingresar IDs de organización válidos (números separados por comas)');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post('/api/network/consultation', {
        organizationIds: ids
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      setResults(response.data);
    } catch (err) {
      console.error('Error in SOAP consultation:', err);
      setError(
        err.response?.data?.message || 
        err.message || 
        'Error al consultar la red de ONGs'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAccordionChange = (orgId) => (event, isExpanded) => {
    setExpandedOrg(isExpanded ? orgId : false);
  };

  if (!hasPermission) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          No tienes permisos para acceder a la consulta de red. 
          Solo los Presidentes pueden acceder a esta funcionalidad.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Consulta de Red de ONGs
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Consultar Organizaciones
        </Typography>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="IDs de Organizaciones"
              placeholder="Ej: 1, 2, 3, 4"
              value={organizationIds}
              onChange={(e) => setOrganizationIds(e.target.value)}
              helperText="Ingresa los IDs de las organizaciones separados por comas"
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
              onClick={handleConsultation}
              disabled={loading || !organizationIds.trim()}
              sx={{ height: 56 }}
            >
              {loading ? 'Consultando...' : 'Consultar'}
            </Button>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {results && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Resultados de la Consulta
          </Typography>

          {results.organizations && results.organizations.length === 0 && (
            <Alert severity="info">
              No se encontraron organizaciones con los IDs proporcionados.
            </Alert>
          )}

          {results.organizations && results.organizations.map((org) => (
            <Accordion
              key={org.id}
              expanded={expandedOrg === org.id}
              onChange={handleAccordionChange(org.id)}
              sx={{ mb: 1 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <BusinessIcon color="primary" />
                  <Typography variant="h6" sx={{ flex: 1 }}>
                    {org.nombre || `Organización ${org.id}`}
                  </Typography>
                  <Chip
                    label={`ID: ${org.id}`}
                    size="small"
                    variant="outlined"
                  />
                  {org.presidente && (
                    <Chip
                      label="Con Presidente"
                      size="small"
                      color="success"
                    />
                  )}
                </Box>
              </AccordionSummary>
              
              <AccordionDetails>
                <Grid container spacing={3}>
                  {/* Organization Details */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BusinessIcon />
                      Información de la Organización
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell component="th" scope="row">ID</TableCell>
                            <TableCell>{org.id}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell component="th" scope="row">Nombre</TableCell>
                            <TableCell>{org.nombre || 'No disponible'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell component="th" scope="row">Descripción</TableCell>
                            <TableCell>{org.descripcion || 'No disponible'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell component="th" scope="row">Dirección</TableCell>
                            <TableCell>{org.direccion || 'No disponible'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell component="th" scope="row">Teléfono</TableCell>
                            <TableCell>{org.telefono || 'No disponible'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell component="th" scope="row">Email</TableCell>
                            <TableCell>{org.email || 'No disponible'}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>

                  {/* President Details */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PersonIcon />
                      Información del Presidente
                    </Typography>
                    {org.presidente ? (
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell component="th" scope="row">ID</TableCell>
                              <TableCell>{org.presidente.id}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Nombre</TableCell>
                              <TableCell>{org.presidente.nombre || 'No disponible'}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Email</TableCell>
                              <TableCell>{org.presidente.email || 'No disponible'}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Teléfono</TableCell>
                              <TableCell>{org.presidente.telefono || 'No disponible'}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Organización ID</TableCell>
                              <TableCell>{org.presidente.organizacion_id}</TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Alert severity="warning">
                        No se encontró información del presidente para esta organización.
                      </Alert>
                    )}
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}

          {/* Summary */}
          {results.organizations && results.organizations.length > 0 && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
              <Typography variant="h6" color="primary.contrastText" gutterBottom>
                Resumen de la Consulta
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="primary.contrastText">
                    {results.organizations.length}
                  </Typography>
                  <Typography variant="body2" color="primary.contrastText">
                    Organizaciones Encontradas
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="primary.contrastText">
                    {results.organizations.filter(org => org.presidente).length}
                  </Typography>
                  <Typography variant="body2" color="primary.contrastText">
                    Con Presidente Asignado
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="primary.contrastText">
                    {results.organizations.filter(org => org.email).length}
                  </Typography>
                  <Typography variant="body2" color="primary.contrastText">
                    Con Email Registrado
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="primary.contrastText">
                    {results.organizations.filter(org => org.telefono).length}
                  </Typography>
                  <Typography variant="body2" color="primary.contrastText">
                    Con Teléfono Registrado
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default NetworkConsultation;