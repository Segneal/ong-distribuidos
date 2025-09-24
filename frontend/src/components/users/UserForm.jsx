import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { usersService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const UserForm = ({ user, onSave, onCancel, isEditing = false }) => {
  const [formData, setFormData] = useState({
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: 'VOLUNTARIO'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  const { user: currentUser } = useAuth();

  useEffect(() => {
    if (isEditing && user) {
      setFormData({
        username: user.username || '',
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.email || '',
        phone: user.phone || '',
        role: user.role || 'VOLUNTARIO'
      });
    }
  }, [user, isEditing]);

  const validateForm = () => {
    const errors = {};

    // Validar username
    if (!formData.username.trim()) {
      errors.username = 'El nombre de usuario es requerido';
    } else if (formData.username.length < 3) {
      errors.username = 'El nombre de usuario debe tener al menos 3 caracteres';
    }

    // Validar nombre
    if (!formData.firstName.trim()) {
      errors.firstName = 'El nombre es requerido';
    }

    // Validar apellido
    if (!formData.lastName.trim()) {
      errors.lastName = 'El apellido es requerido';
    }

    // Validar email
    if (!formData.email.trim()) {
      errors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'El email no tiene un formato válido';
    }

    // Validar teléfono (opcional pero si se proporciona debe ser válido)
    if (formData.phone && !/^\+?[\d\s\-\(\)]+$/.test(formData.phone)) {
      errors.phone = 'El teléfono no tiene un formato válido';
    }

    // Validar rol
    if (!['PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO'].includes(formData.role)) {
      errors.role = 'Debe seleccionar un rol válido';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Limpiar error de validación cuando el usuario empiece a escribir
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response;
      
      if (isEditing && user) {
        response = await usersService.updateUser(user.id, formData);
      } else {
        response = await usersService.createUser(formData);
      }

      if (response.data.success) {
        if (onSave) {
          onSave(response.data.user);
        }
        
        // Limpiar formulario si es creación
        if (!isEditing) {
          setFormData({
            username: '',
            firstName: '',
            lastName: '',
            email: '',
            phone: '',
            role: 'VOLUNTARIO'
          });
        }
      } else {
        setError(response.data.error || 'Error al guardar usuario');
      }
    } catch (err) {
      console.error('Error saving user:', err);
      setError(err.response?.data?.error || 'Error al guardar usuario');
    } finally {
      setLoading(false);
    }
  };

  const getRoleOptions = () => {
    return [
      { value: 'PRESIDENTE', label: 'Presidente' },
      { value: 'VOCAL', label: 'Vocal' },
      { value: 'COORDINADOR', label: 'Coordinador' },
      { value: 'VOLUNTARIO', label: 'Voluntario' }
    ];
  };

  // Solo PRESIDENTE puede gestionar usuarios
  if (currentUser?.role !== 'PRESIDENTE') {
    return (
      <Alert severity="warning">
        No tienes permisos para gestionar usuarios.
      </Alert>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h4" component="h2" gutterBottom>
        {isEditing ? 'Editar Usuario' : 'Crear Nuevo Usuario'}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Nombre de Usuario"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              error={!!validationErrors.username}
              helperText={validationErrors.username}
              disabled={loading}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth error={!!validationErrors.role} disabled={loading}>
              <InputLabel>Rol *</InputLabel>
              <Select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                label="Rol *"
              >
                {getRoleOptions().map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
              {validationErrors.role && (
                <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                  {validationErrors.role}
                </Typography>
              )}
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Nombre"
              name="firstName"
              value={formData.firstName}
              onChange={handleInputChange}
              error={!!validationErrors.firstName}
              helperText={validationErrors.firstName}
              disabled={loading}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Apellido"
              name="lastName"
              value={formData.lastName}
              onChange={handleInputChange}
              error={!!validationErrors.lastName}
              helperText={validationErrors.lastName}
              disabled={loading}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              error={!!validationErrors.email}
              helperText={validationErrors.email}
              disabled={loading}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Teléfono"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleInputChange}
              error={!!validationErrors.phone}
              helperText={validationErrors.phone || "Opcional"}
              disabled={loading}
            />
          </Grid>

          {!isEditing && (
            <Grid item xs={12}>
              <Alert severity="info">
                <strong>Nota:</strong> Se generará una contraseña aleatoria y se enviará por email al usuario.
              </Alert>
            </Grid>
          )}

          <Grid item xs={12}>
            <Box display="flex" gap={2} mt={2}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : (isEditing ? <SaveIcon /> : <AddIcon />)}
              >
                {loading ? (isEditing ? 'Actualizando...' : 'Creando...') : (isEditing ? 'Actualizar Usuario' : 'Crear Usuario')}
              </Button>
              
              <Button
                type="button"
                variant="outlined"
                onClick={onCancel}
                disabled={loading}
                startIcon={<CancelIcon />}
              >
                Cancelar
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default UserForm;