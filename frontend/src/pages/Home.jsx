import React from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Grid, 
  Card, 
  CardContent,
  CardActions,
  Button
} from '@mui/material';
import {
  People as PeopleIcon,
  Inventory as InventoryIcon,
  Event as EventIcon,
  NetworkCheck as NetworkIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const { user, hasPermission } = useAuth();

  const allFeatures = [
    {
      title: 'Gestión de Usuarios',
      description: 'Administra los miembros de la organización con diferentes roles.',
      icon: <PeopleIcon fontSize="large" color="primary" />,
      path: '/users',
      permission: () => user?.role === 'PRESIDENTE'
    },
    {
      title: 'Inventario de Donaciones',
      description: 'Controla y gestiona las donaciones recibidas por categorías.',
      icon: <InventoryIcon fontSize="large" color="primary" />,
      path: '/inventory',
      permission: () => user?.role === 'PRESIDENTE' || user?.role === 'VOCAL'
    },
    {
      title: 'Eventos Solidarios',
      description: 'Organiza y coordina eventos solidarios con participantes.',
      icon: <EventIcon fontSize="large" color="primary" />,
      path: '/events',
      permission: () => true // Todos pueden ver eventos
    }
  ];

  // Filtrar características según permisos
  const features = allFeatures.filter(feature => feature.permission());

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Bienvenido al Sistema de Gestión
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom align="center" color="text.secondary">
          ONG Empuje Comunitario
        </Typography>
        <Typography variant="body1" align="center" sx={{ mt: 2 }}>
          Sistema integral para la administración de usuarios, inventario de donaciones 
          y eventos solidarios, con integración a la red de ONGs colaborativas.
        </Typography>
      </Paper>

      <Grid container spacing={3} justifyContent="center">
        {features.map((feature, index) => {
          // Calcular el tamaño de grid basado en el número de features
          const gridSize = features.length === 1 ? 12 : 
                          features.length === 2 ? 6 : 
                          features.length === 3 ? 4 : 3;
          
          return (
            <Grid item xs={12} sm={6} md={gridSize} key={index}>
              <Card sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                minHeight: '280px'
              }}>
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                  <Box sx={{ mb: 3 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600 }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                    {feature.description}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 3 }}>
                  <Button 
                    size="large" 
                    variant="contained"
                    onClick={() => window.location.href = feature.path}
                    sx={{ 
                      px: 4, 
                      py: 1.5,
                      borderRadius: 2,
                      textTransform: 'none',
                      fontSize: '1rem'
                    }}
                  >
                    Acceder
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      
    </Box>
  );
};

export default Home;