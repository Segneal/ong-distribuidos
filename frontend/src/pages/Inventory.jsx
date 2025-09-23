import React from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Alert,
  Button,
  Grid,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import { 
  Add as AddIcon, 
  Inventory as InventoryIcon,
  Checkroom as RopaIcon,
  Restaurant as AlimentosIcon,
  Toys as JuguetesIcon,
  School as UtilesIcon
} from '@mui/icons-material';

const Inventory = () => {
  const categories = [
    { name: 'ROPA', icon: <RopaIcon />, count: 0, color: 'primary' },
    { name: 'ALIMENTOS', icon: <AlimentosIcon />, count: 0, color: 'secondary' },
    { name: 'JUGUETES', icon: <JuguetesIcon />, count: 0, color: 'success' },
    { name: 'ÚTILES ESCOLARES', icon: <UtilesIcon />, count: 0, color: 'warning' }
  ];

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <InventoryIcon sx={{ mr: 2 }} color="primary" />
          <Typography variant="h4" component="h1">
            Inventario de Donaciones
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Gestiona las donaciones recibidas organizadas por categorías.
        </Typography>
      </Paper>

      <Alert severity="info" sx={{ mb: 3 }}>
        La gestión de inventario será implementada en una tarea posterior. 
        Aquí podrás registrar, modificar y eliminar donaciones del inventario.
      </Alert>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {categories.map((category, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Box sx={{ mb: 2, color: `${category.color}.main` }}>
                  {category.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {category.name}
                </Typography>
                <Chip 
                  label={`${category.count} items`} 
                  color={category.color}
                  variant="outlined"
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper elevation={1} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            Donaciones Registradas
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            disabled
          >
            Nueva Donación
          </Button>
        </Box>

        <Box textAlign="center" py={4}>
          <Typography variant="body2" color="text.secondary">
            No hay donaciones registradas. La funcionalidad será implementada próximamente.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Inventory;