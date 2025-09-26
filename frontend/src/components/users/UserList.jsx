import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  FormControlLabel,
  Switch,
  Tooltip
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Email as EmailIcon
} from '@mui/icons-material';
import { usersService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import SendCredentialsModal from './SendCredentialsModal';

const UserList = ({ onEditUser, onDeleteUser }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [includeInactive, setIncludeInactive] = useState(false);
  const [credentialsModal, setCredentialsModal] = useState({ open: false, user: null });
  const { user } = useAuth();



  useEffect(() => {
    loadUsers();
  }, [includeInactive]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await usersService.getUsers({ includeInactive });
      
      if (response.data.success) {
        setUsers(response.data.users || []);
      } else {
        setError(response.data.error || 'Error al cargar usuarios');
      }
    } catch (err) {
      console.error('Error loading users:', err);
      setError(err.response?.data?.error || 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId, userName) => {
    if (window.confirm(`¿Estás seguro de que deseas eliminar al usuario "${userName}"?`)) {
      try {
        const response = await usersService.deleteUser(userId);
        
        if (response.data.success) {
          // Recargar la lista de usuarios
          loadUsers();
          if (onDeleteUser) {
            onDeleteUser(userId);
          }
        } else {
          setError(response.data.error || 'Error al eliminar usuario');
        }
      } catch (err) {
        console.error('Error deleting user:', err);
        setError(err.response?.data?.error || 'Error al eliminar usuario');
      }
    }
  };

  const handleSendCredentials = (user) => {
    setCredentialsModal({ open: true, user });
  };

  const handleCloseCredentialsModal = () => {
    setCredentialsModal({ open: false, user: null });
  };



  const getStatusChip = (isActive) => {
    return (
      <Chip
        label={isActive ? 'Activo' : 'Inactivo'}
        color={isActive ? 'success' : 'default'}
        size="small"
      />
    );
  };

  const getRoleChip = (role) => {
    const roleConfig = {
      'PRESIDENTE': { color: 'primary', label: 'Presidente' },
      'VOCAL': { color: 'info', label: 'Vocal' },
      'COORDINADOR': { color: 'warning', label: 'Coordinador' },
      'VOLUNTARIO': { color: 'default', label: 'Voluntario' }
    };
    
    const config = roleConfig[role] || { color: 'default', label: role };
    
    return (
      <Chip
        label={config.label}
        color={config.color}
        size="small"
      />
    );
  };

  // Solo PRESIDENTE puede ver la lista de usuarios
  if (user?.role !== 'PRESIDENTE') {
    return (
      <Alert severity="warning">
        No tienes permisos para ver la lista de usuarios. Usuario actual: {user?.username || 'No autenticado'}, Rol: {user?.role || 'Sin rol'}
      </Alert>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Gestión de Usuarios
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
            />
          }
          label="Incluir usuarios inactivos"
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {users.length === 0 ? (
        <Alert severity="info">
          No se encontraron usuarios.
        </Alert>
      ) : (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Usuario</TableCell>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Teléfono</TableCell>
                  <TableCell>Rol</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Fecha Creación</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.firstName} {user.lastName}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.phone || '-'}</TableCell>
                    <TableCell>{getRoleChip(user.role)}</TableCell>
                    <TableCell>{getStatusChip(user.isActive)}</TableCell>
                    <TableCell>{new Date(user.createdAt).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="Editar usuario">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => onEditUser && onEditUser(user)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Enviar email de bienvenida">
                          <IconButton
                            size="small"
                            color="info"
                            onClick={() => handleSendCredentials(user)}
                            disabled={!user.isActive || !user.email}
                          >
                            <EmailIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Eliminar usuario">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteUser(user.id, user.username)}
                            disabled={!user.isActive}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <Box p={2}>
            <Typography variant="body2" color="text.secondary">
              Total de usuarios: {users.length}
            </Typography>
          </Box>
        </Paper>
      )}

      <SendCredentialsModal
        open={credentialsModal.open}
        onClose={handleCloseCredentialsModal}
        user={credentialsModal.user}
      />
    </Box>
  );
};

export default UserList;