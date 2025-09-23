import React from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Alert,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip
} from '@mui/material';
import { 
  Add as AddIcon, 
  Event as EventIcon,
  CalendarToday as CalendarIcon,
  People as PeopleIcon
} from '@mui/icons-material';

const Events = () => {
  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <EventIcon sx={{ mr: 2 }} color="primary" />
          <Typography variant="h4" component="h1">
            Eventos Solidarios
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Organiza y coordina eventos solidarios con participantes de la organización.
        </Typography>
      </Paper>

      <Alert severity="info" sx={{ mb: 3 }}>
        La gestión de eventos será implementada en una tarea posterior. 
        Aquí podrás crear, modificar eventos y gestionar participantes.
      </Alert>

      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            Próximos Eventos
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            disabled
          >
            Nuevo Evento
          </Button>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card sx={{ opacity: 0.6 }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <CalendarIcon sx={{ mr: 1 }} color="primary" />
                  <Typography variant="h6">
                    Evento de Ejemplo
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Descripción del evento solidario que se realizará próximamente.
                </Typography>
                <Box display="flex" alignItems="center" mt={2}>
                  <PeopleIcon sx={{ mr: 1, fontSize: 'small' }} />
                  <Chip label="0 participantes" size="small" variant="outlined" />
                </Box>
              </CardContent>
              <CardActions>
                <Button size="small" disabled>Ver Detalles</Button>
                <Button size="small" disabled>Editar</Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>

        <Box textAlign="center" py={4}>
          <Typography variant="body2" color="text.secondary">
            No hay eventos programados. La funcionalidad será implementada próximamente.
          </Typography>
        </Box>
      </Paper>

      <Paper elevation={1} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Eventos Pasados
        </Typography>
        <Box textAlign="center" py={4}>
          <Typography variant="body2" color="text.secondary">
            No hay eventos pasados registrados.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Events;