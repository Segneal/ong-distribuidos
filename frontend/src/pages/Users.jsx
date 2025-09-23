import React from 'react';
import { 
  Typography, 
  Paper, 
  Box, 
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { Add as AddIcon, People as PeopleIcon } from '@mui/icons-material';

const Users = () => {
  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <PeopleIcon sx={{ mr: 2 }} color="primary" />
          <Typography variant="h4" component="h1">
            Gestión de Usuarios
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Administra los miembros de la organización y sus roles.
        </Typography>
      </Paper>

      <Alert severity="info" sx={{ mb: 3 }}>
        La gestión de usuarios será implementada en una tarea posterior. 
        Aquí podrás crear, modificar y eliminar usuarios del sistema.
      </Alert>

      <Paper elevation={1} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            Lista de Usuarios
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            disabled
          >
            Nuevo Usuario
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre de Usuario</TableCell>
                <TableCell>Nombre Completo</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Rol</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No hay usuarios para mostrar. La funcionalidad será implementada próximamente.
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Users;