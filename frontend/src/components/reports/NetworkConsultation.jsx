import React, { useState } from 'react';
import { useQuery, useLazyQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import BusinessIcon from '@mui/icons-material/Business';
import PersonIcon from '@mui/icons-material/Person';

// GraphQL Queries
const NETWORK_CONSULTATION_QUERY = gql`
  query NetworkConsultation($organizationIds: [Int!]!) {
    networkConsultation(organizationIds: $organizationIds) {
      presidents {
        organizationId
        presidentName
        presidentEmail
        presidentPhone
        presidentId
        presidentAddress
        startDate
        status
      }
      organizations {
        organizationId
        organizationName
        organizationType
        address
        city
        country
        phone
        email
        website
        registrationDate
        status
        description
      }
      queryIds
      totalPresidents
      totalOrganizations
      errors
    }
  }
`;

const SOAP_CONNECTION_TEST_QUERY = gql`
  query SoapConnectionTest {
    soapConnectionTest {
      connected
      serviceUrl
      message
    }
  }
`;

const NetworkConsultation = () => {
  const [organizationIds, setOrganizationIds] = useState('');
  const [consultationData, setConsultationData] = useState(null);

  // Connection test query
  const { data: connectionTest, loading: testLoading } = useQuery(SOAP_CONNECTION_TEST_QUERY);

  // Network consultation lazy query
  const [executeConsultation, { loading: consultationLoading, error: consultationError }] = useLazyQuery(
    NETWORK_CONSULTATION_QUERY,
    {
      onCompleted: (data) => {
        setConsultationData(data.networkConsultation);
      },
      onError: (error) => {
        console.error('Error en consulta de red:', error);
      }
    }
  );

  const handleConsultation = () => {
    if (!organizationIds.trim()) {
      alert('Por favor ingrese al menos un ID de organización');
      return;
    }

    // Parse organization IDs from comma-separated string
    const ids = organizationIds
      .split(',')
      .map(id => parseInt(id.trim()))
      .filter(id => !isNaN(id) && id > 0);

    if (ids.length === 0) {
      alert('Por favor ingrese IDs de organización válidos (números enteros positivos)');
      return;
    }

    executeConsultation({
      variables: { organizationIds: ids }
    });
  };

  const handleClearResults = () => {
    setConsultationData(null);
    setOrganizationIds('');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Consulta de Red de ONGs
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Consulte información de presidentes y organizaciones de la red de ONGs mediante sus IDs.
      </Typography>

      {/* Connection Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Estado de Conexión SOAP
          </Typography>
          {testLoading ? (
            <CircularProgress size={20} />
          ) : connectionTest?.soapConnectionTest ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                label={connectionTest.soapConnectionTest.connected ? 'Conectado' : 'Desconectado'}
                color={connectionTest.soapConnectionTest.connected ? 'success' : 'error'}
                size="small"
              />
              <Typography variant="body2" color="text.secondary">
                {connectionTest.soapConnectionTest.message}
              </Typography>
            </Box>
          ) : (
            <Alert severity="warning">No se pudo verificar el estado de conexión</Alert>
          )}
        </CardContent>
      </Card>

      {/* Query Form */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Consultar Organizaciones
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="IDs de Organizaciones"
                placeholder="Ej: 5, 6, 8, 10"
                value={organizationIds}
                onChange={(e) => setOrganizationIds(e.target.value)}
                helperText="Ingrese los IDs separados por comas"
                disabled={consultationLoading}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleConsultation}
                disabled={consultationLoading || !connectionTest?.soapConnectionTest?.connected}
                sx={{ height: '56px' }}
              >
                {consultationLoading ? <CircularProgress size={20} /> : 'Consultar'}
              </Button>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleClearResults}
                disabled={consultationLoading}
                sx={{ height: '56px' }}
              >
                Limpiar
              </Button>
            </Grid>
          </Grid>

          {consultationError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Error en la consulta: {consultationError.message}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {consultationData && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Resultados de la Consulta
            </Typography>

            {/* Summary */}
            <Box sx={{ mb: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {consultationData.totalOrganizations}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Organizaciones
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="secondary">
                      {consultationData.totalPresidents}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Presidentes
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    IDs consultados: {consultationData.queryIds.join(', ')}
                  </Typography>
                </Grid>
              </Grid>
            </Box>

            {/* Errors */}
            {consultationData.errors && consultationData.errors.length > 0 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Advertencias:</Typography>
                <ul>
                  {consultationData.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </Alert>
            )}

            <Divider sx={{ my: 2 }} />

            {/* Organizations Section */}
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <BusinessIcon sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Organizaciones ({consultationData.totalOrganizations})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {consultationData.organizations.length > 0 ? (
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Nombre</TableCell>
                          <TableCell>Tipo</TableCell>
                          <TableCell>Dirección</TableCell>
                          <TableCell>Teléfono</TableCell>
                          <TableCell>Estado</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {consultationData.organizations.map((org) => (
                          <TableRow key={org.organizationId}>
                            <TableCell>{org.organizationId}</TableCell>
                            <TableCell>
                              <Typography variant="subtitle2">
                                {org.organizationName}
                              </Typography>
                            </TableCell>
                            <TableCell>{org.organizationType}</TableCell>
                            <TableCell>{org.address}</TableCell>
                            <TableCell>{org.phone}</TableCell>
                            <TableCell>
                              <Chip 
                                label={org.status || 'Activo'} 
                                color="success" 
                                size="small" 
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Alert severity="info">No se encontraron organizaciones</Alert>
                )}
              </AccordionDetails>
            </Accordion>

            {/* Presidents Section */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <PersonIcon sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Presidentes ({consultationData.totalPresidents})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {consultationData.presidents.length > 0 ? (
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>ID Presidente</TableCell>
                          <TableCell>Nombre</TableCell>
                          <TableCell>Organización ID</TableCell>
                          <TableCell>Teléfono</TableCell>
                          <TableCell>Dirección</TableCell>
                          <TableCell>Estado</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {consultationData.presidents.map((president) => (
                          <TableRow key={president.presidentId}>
                            <TableCell>{president.presidentId}</TableCell>
                            <TableCell>
                              <Typography variant="subtitle2">
                                {president.presidentName}
                              </Typography>
                            </TableCell>
                            <TableCell>{president.organizationId}</TableCell>
                            <TableCell>{president.presidentPhone}</TableCell>
                            <TableCell>{president.presidentAddress}</TableCell>
                            <TableCell>
                              <Chip 
                                label={president.status || 'Activo'} 
                                color="success" 
                                size="small" 
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Alert severity="info">No se encontraron presidentes</Alert>
                )}
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default NetworkConsultation;