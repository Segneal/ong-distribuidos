import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton
} from '@mui/material';
import {
  Login as LoginIcon,
  Visibility,
  VisibilityOff,
  Person,
  Lock
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const LoginForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, error, clearError } = useAuth();

  // Estado del formulario
  const [formData, setFormData] = useState({
    usernameOrEmail: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({});

  // Obtener la ruta a la que debe redirigir después del login
  const from = location.state?.from?.pathname || '/';

  // Manejar cambios en los campos del formulario
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Limpiar errores cuando el usuario empiece a escribir
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }

    // Limpiar error general
    if (error) {
      clearError();
    }
  };

  // Validar formulario
  const validateForm = () => {
    const errors = {};

    if (!formData.usernameOrEmail.trim()) {
      errors.usernameOrEmail = 'Usuario o email es requerido';
    }

    if (!formData.password) {
      errors.password = 'Contraseña es requerida';
    } else if (formData.password.length < 3) {
      errors.password = 'Contraseña debe tener al menos 3 caracteres';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Manejar envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const result = await login(formData);

      if (result.success) {
        // Redirigir según el rol del usuario
        const userRole = result.user.role;
        let redirectPath = from;

        // Si viene de la raíz, redirigir según el rol
        if (from === '/') {
          switch (userRole) {
            case 'PRESIDENTE':
              redirectPath = '/users';
              break;
            case 'VOCAL':
              redirectPath = '/inventory';
              break;
            case 'COORDINADOR':
              redirectPath = '/events';
              break;
            case 'VOLUNTARIO':
              redirectPath = '/events';
              break;
            default:
              redirectPath = '/';
          }
        }

        navigate(redirectPath, { replace: true });
      }
    } catch (error) {
      console.error('Error en login:', error);
    }
  };

  // Alternar visibilidad de contraseña
  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="80vh"
      px={2}
    >
      <Paper elevation={3} sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Box textAlign="center" mb={3}>
          <LoginIcon fontSize="large" color="primary" />
          <Typography variant="h4" component="h1" gutterBottom>
            Sistema Multi-Organización
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Iniciar Sesión
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sistema de Gestión MultiONG
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <TextField
            margin="normal"
            required
            fullWidth
            id="usernameOrEmail"
            label="Usuario o Email"
            name="usernameOrEmail"
            autoComplete="username"
            autoFocus
            value={formData.usernameOrEmail}
            onChange={handleChange}
            error={!!formErrors.usernameOrEmail}
            helperText={formErrors.usernameOrEmail}
            disabled={isLoading}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Person color="action" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Contraseña"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={formData.password}
            onChange={handleChange}
            error={!!formErrors.password}
            helperText={formErrors.password}
            disabled={isLoading}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleTogglePasswordVisibility}
                    edge="end"
                    disabled={isLoading}
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </Button>
        </Box>

        <Typography variant="body2" color="text.secondary" align="center">
          © 2025 Sistema de Gestión MultiONG
        </Typography>
      </Paper>
    </Box>
  );
};

export default LoginForm;