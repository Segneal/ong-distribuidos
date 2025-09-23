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

const Home = () => {
  const features = [
    {
      title: 'Gestión de Usuarios',
      description: 'Administra los miembros de la organización con diferentes roles.',
      icon: <PeopleIcon fontSize="large" color="primary" />,
      path: '/users'
    },
    {
      title: 'Inventario de Donaciones',
      description: 'Controla y gestiona las donaciones recibidas por categorías.',
      icon: <InventoryIcon fontSize="large" color="primary" />,
      path: '/inventory'
    },
    {
      title: 'Eventos Solidarios',
      description: 'Organiza y coordina eventos solidarios con participantes.',
      icon: <EventIcon fontSize="large" color="primary" />,
      path: '/events'
    },
    {
      title: 'Red de ONGs',
      description: 'Colabora con otras organizaciones a través de la red.',
      icon: <NetworkIcon fontSize="large" color="primary" />,
      path: '/network'
    }
  ];

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

      <Paper elevation={1} sx={{ p: 3, mt: 4, bgcolor: 'grey.50' }}>
        <Typography variant="h6" gutterBottom>
          Estado del Sistema
        </Typography>
        <Typography variant="body2" color="text.secondary">
          ✅ API Gateway: Configurado<br />
          🔄 Microservicios: En desarrollo<br />
          🔄 Frontend: En desarrollo<br />
          ⏳ Autenticación: Pendiente
        </Typography>
      </Paper>
    </Box>
  );
};

export default Home;