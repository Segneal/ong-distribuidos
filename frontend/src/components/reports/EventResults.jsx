import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Card,
  CardContent
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { formatDate, formatCurrency } from '../../utils/helpers';

const EventResults = ({ data, selectedUser }) => {
  const [expandedMonth, setExpandedMonth] = useState(false);

  const handleAccordionChange = (month) => (event, isExpanded) => {
    setExpandedMonth(isExpanded ? month : false);
  };

  if (!data || data.length === 0) {
    return (
      <Alert severity="info">
        No se encontraron eventos con los filtros aplicados.
      </Alert>
    );
  }

  // Calculate totals
  const totalEvents = data.reduce((sum, monthGroup) => sum + monthGroup.eventos.length, 0);
  const totalDonations = data.reduce((sum, monthGroup) => 
    sum + monthGroup.eventos.reduce((eventSum, event) => 
      eventSum + event.donaciones.reduce((donSum, donation) => donSum + donation.cantidad, 0), 0
    ), 0
  );

  return (
    <Box>
      {/* Summary Card */}
      <Card sx={{ mb: 3, bgcolor: 'primary.light' }}>
        <CardContent>
          <Typography variant="h6" color="primary.contrastText" gutterBottom>
            Resumen de Participación - {selectedUser?.nombre}
          </Typography>
          <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            <Box>
              <Typography variant="h4" color="primary.contrastText">
                {totalEvents}
              </Typography>
              <Typography variant="body2" color="primary.contrastText">
                Eventos Participados
              </Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="primary.contrastText">
                {data.length}
              </Typography>
              <Typography variant="body2" color="primary.contrastText">
                Meses con Actividad
              </Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="primary.contrastText">
                {formatCurrency(totalDonations)}
              </Typography>
              <Typography variant="body2" color="primary.contrastText">
                Total en Donaciones
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Monthly Results */}
      {data.map((monthGroup) => {
        const monthDonations = monthGroup.eventos.reduce((sum, event) => 
          sum + event.donaciones.reduce((donSum, donation) => donSum + donation.cantidad, 0), 0
        );

        return (
          <Accordion
            key={monthGroup.mes}
            expanded={expandedMonth === monthGroup.mes}
            onChange={handleAccordionChange(monthGroup.mes)}
            sx={{ mb: 1 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Typography variant="h6" sx={{ flex: 1 }}>
                  {monthGroup.mes}
                </Typography>
                <Typography variant="body1" color="primary">
                  {formatCurrency(monthDonations)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ({monthGroup.eventos.length} eventos)
                </Typography>
              </Box>
            </AccordionSummary>
            
            <AccordionDetails>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Día</TableCell>
                      <TableCell>Nombre del Evento</TableCell>
                      <TableCell>Descripción</TableCell>
                      <TableCell align="center">Donaciones</TableCell>
                      <TableCell align="right">Total Donaciones</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {monthGroup.eventos.map((event, index) => {
                      const eventDonations = event.donaciones.reduce((sum, donation) => sum + donation.cantidad, 0);
                      
                      return (
                        <TableRow key={`${monthGroup.mes}-${index}`}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="bold">
                              {event.dia}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {event.nombre}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {event.descripcion || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={event.donaciones.length}
                              size="small"
                              color={event.donaciones.length > 0 ? 'success' : 'default'}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight="medium">
                              {formatCurrency(eventDonations)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Detailed donations for the month */}
              {monthGroup.eventos.some(event => event.donaciones.length > 0) && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Detalle de Donaciones del Mes
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Evento</TableCell>
                          <TableCell>Categoría</TableCell>
                          <TableCell>Descripción</TableCell>
                          <TableCell align="right">Cantidad</TableCell>
                          <TableCell align="center">Estado</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {monthGroup.eventos.flatMap(event => 
                          event.donaciones.map((donation, donIndex) => (
                            <TableRow key={`${event.nombre}-${donIndex}`}>
                              <TableCell>
                                <Typography variant="caption">
                                  {event.nombre}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Chip label={donation.categoria} size="small" variant="outlined" />
                              </TableCell>
                              <TableCell>
                                {donation.descripcion || '-'}
                              </TableCell>
                              <TableCell align="right">
                                {formatCurrency(donation.cantidad)}
                              </TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={donation.eliminado ? 'Eliminado' : 'Activo'}
                                  color={donation.eliminado ? 'error' : 'success'}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Box>
  );
};

export default EventResults;