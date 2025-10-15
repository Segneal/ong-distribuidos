import React, { useState } from 'react';
import {
  Button,
  CircularProgress,
  Alert,
  Snackbar,
  Box,
  Typography
} from '@mui/material';
import {
  FileDownload as FileDownloadIcon,
  GetApp as GetAppIcon
} from '@mui/icons-material';
import axios from 'axios';

const ExcelExport = ({ filters }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleExport = async () => {
    if (!filters) {
      setError('No hay filtros aplicados para exportar');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Call the REST API to generate Excel file
      const response = await axios.post('/api/reports/donations/excel', {
        filtros: filters
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.downloadUrl) {
        // Trigger download
        const downloadResponse = await axios.get(response.data.downloadUrl, {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        // Create download link
        const url = window.URL.createObjectURL(new Blob([downloadResponse.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', response.data.fileName || 'reporte_donaciones.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        setSuccess(true);
      } else {
        throw new Error('No se recibió URL de descarga');
      }
    } catch (err) {
      console.error('Error exporting to Excel:', err);
      setError(
        err.response?.data?.message || 
        err.message || 
        'Error al generar el archivo Excel'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  const handleCloseSuccess = () => {
    setSuccess(false);
  };

  return (
    <Box>
      <Button
        variant="contained"
        color="success"
        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <FileDownloadIcon />}
        onClick={handleExport}
        disabled={loading || !filters}
        sx={{ minWidth: 160 }}
      >
        {loading ? 'Generando...' : 'Exportar Excel'}
      </Button>

      {loading && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Generando archivo Excel, por favor espera...
          </Typography>
        </Box>
      )}

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      {/* Success Snackbar */}
      <Snackbar
        open={success}
        autoHideDuration={4000}
        onClose={handleCloseSuccess}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSuccess} severity="success" sx={{ width: '100%' }}>
          Archivo Excel descargado exitosamente
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ExcelExport;