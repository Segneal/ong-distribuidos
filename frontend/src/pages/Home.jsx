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

      <Grid container spacing={3}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" component="h3" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button 
                  size="small" 
                  variant="outlined"
                  onClick={() => window.location.href = feature.path}
                >
                  Acceder
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      
    </Box>
  );
};

export default Home;