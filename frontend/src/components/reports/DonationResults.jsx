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
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { formatDate, formatCurrency } from '../../utils/helpers';

const DonationResults = ({ data }) => {
  const [expandedCategory, setExpandedCategory] = useState(false);

  const handleAccordionChange = (category) => (event, isExpanded) => {
    setExpandedCategory(isExpanded ? category : false);
  };

  if (!data || data.length === 0) {
    return (
      <Alert severity="info">
        No se encontraron donaciones con los filtros aplicados.
      </Alert>
    );
  }

  // Calculate total across all categories
  const grandTotal = data.reduce((sum, categoryGroup) => sum + categoryGroup.totalCantidad, 0);

  return (
    <Box>
      <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
        <Typography variant="h6" color="primary.contrastText">
          Total General: {formatCurrency(grandTotal)}
        </Typography>
        <Typography variant="body2" color="primary.contrastText">
          {data.length} categoría(s) encontrada(s)
        </Typography>
      </Box>

      {data.map((categoryGroup) => (
        <Accordion
          key={`${categoryGroup.categoria}-${categoryGroup.eliminado}`}
          expanded={expandedCategory === `${categoryGroup.categoria}-${categoryGroup.eliminado}`}
          onChange={handleAccordionChange(`${categoryGroup.categoria}-${categoryGroup.eliminado}`)}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Typography variant="h6" sx={{ flex: 1 }}>
                {categoryGroup.categoria}
              </Typography>
              <Chip
                label={categoryGroup.eliminado ? 'Eliminados' : 'Activos'}
                color={categoryGroup.eliminado ? 'error' : 'success'}
                size="small"
              />
              <Typography variant="h6" color="primary">
                {formatCurrency(categoryGroup.totalCantidad)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ({categoryGroup.registros.length} registros)
              </Typography>
            </Box>
          </AccordionSummary>
          
          <AccordionDetails>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Fecha Alta</TableCell>
                    <TableCell>Descripción</TableCell>
                    <TableCell align="right">Cantidad</TableCell>
                    <TableCell>Usuario Alta</TableCell>
                    <TableCell>Fecha Modificación</TableCell>
                    <TableCell>Usuario Modificación</TableCell>
                    <TableCell align="center">Estado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {categoryGroup.registros.map((donation) => (
                    <TableRow key={donation.id}>
                      <TableCell>
                        {formatDate(donation.fechaAlta)}
                      </TableCell>
                      <TableCell>
                        {donation.descripcion || '-'}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(donation.cantidad)}
                      </TableCell>
                      <TableCell>
                        {donation.usuarioAlta?.nombre || '-'}
                      </TableCell>
                      <TableCell>
                        {donation.fechaModificacion ? formatDate(donation.fechaModificacion) : '-'}
                      </TableCell>
                      <TableCell>
                        {donation.usuarioModificacion?.nombre || '-'}
                      </TableCell>
                      <TableCell align="center">
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
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default DonationResults;