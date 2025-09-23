import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Typography, 
  Paper, 
  Box, 
  Button 
} from '@mui/material';
import { Home as HomeIcon, Error as ErrorIcon } from '@mui/icons-material';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center', maxWidth: 500 }}>
        <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
        
        <Typography variant="h3" component="h1" gutterBottom>
          404
        </Typography>
        
        <Typography variant="h5" component="h2" gutterBottom color="text.secondary">
          Página no encontrada
        </Typography>
        
        <Typography variant="body1" sx={{ mb: 3 }} color="text.secondary">
          La página que estás buscando no existe o ha sido movida.
        </Typography>
        
        <Button
          variant="contained"
          startIcon={<HomeIcon />}
          onClick={() => navigate('/')}
          size="large"
        >
          Volver al Inicio
        </Button>
      </Paper>
    </Box>
  );
};

export default NotFound;