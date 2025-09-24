import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  People as PeopleIcon
} from '@mui/icons-material';
import UserList from '../components/users/UserList';
import UserForm from '../components/users/UserForm';
import { useAuth } from '../contexts/AuthContext';

const Users = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [refreshList, setRefreshList] = useState(0);
  const { user } = useAuth();

  // Solo PRESIDENTE puede acceder a la gestión de usuarios
  if (user?.role !== 'PRESIDENTE') {
    return (
      <Box p={4}>
        <Alert severity="warning">
          <Typography variant="h6">Acceso Denegado</Typography>
          <Typography>No tienes permisos para acceder a la gestión de usuarios.</Typography>
        </Alert>
      </Box>
    );
  }

  const handleCreateUser = () => {
    setEditingUser(null);
    setShowForm(true);
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setShowForm(true);
  };

  const handleDeleteUser = (userId) => {
    // Forzar actualización de la lista
    setRefreshList(prev => prev + 1);
  };

  const handleSaveUser = (savedUser) => {
    setShowForm(false);
    setEditingUser(null);
    // Forzar actualización de la lista
    setRefreshList(prev => prev + 1);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingUser(null);
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box display="flex" alignItems="center" gap={1}>
          <PeopleIcon color="primary" />
          <Typography variant="h4" component="h1">
            Gestión de Usuarios
          </Typography>
        </Box>
        
        {!showForm && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreateUser}
          >
            Nuevo Usuario
          </Button>
        )}
      </Box>

      {showForm ? (
        <UserForm
          user={editingUser}
          onSave={handleSaveUser}
          onCancel={handleCancelForm}
          isEditing={!!editingUser}
        />
      ) : (
        <UserList
          key={refreshList} // Forzar re-render cuando cambie
          onEditUser={handleEditUser}
          onDeleteUser={handleDeleteUser}
        />
      )}
    </Box>
  );
};

export default Users;