import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({ 
  children, 
  requiredRoles = [], 
  requiredPermission = null,
  fallbackPath = '/login' 
}) => {
  const { 
    isLoading, 
    isAuthenticated, 
    user, 
    hasAnyRole, 
    hasPermission 
  } = useAuth();
  const location = useLocation();

  // Mostrar loading mientras se verifica la autenticación
  if (isLoading) {
    return (
      <Box 
        display="flex" 
        flexDirection="column"
        justifyContent="center" 
        alignItems="center" 
        minHeight="60vh"
        gap={2}
      >
        <CircularProgress size={40} />
        <Typography variant="body1" color="text.secondary">
          Verificando autenticación...
        </Typography>
      </Box>
    );
  }

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // Verificar roles requeridos
  if (requiredRoles.length > 0 && !hasAnyRole(requiredRoles)) {
    return (
      <Box p={3}>
        <Alert severity="error">
          <Typography variant="h6" gutterBottom>
            Acceso Denegado
          </Typography>
          <Typography variant="body2">
            No tienes permisos para acceder a esta sección.
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Tu rol actual: <strong>{user?.role}</strong>
          </Typography>
          <Typography variant="body2">
            Roles requeridos: <strong>{requiredRoles.join(', ')}</strong>
          </Typography>
        </Alert>
      </Box>
    );
  }

  // Verificar permisos específicos
  if (requiredPermission) {
    const { resource, action } = requiredPermission;
    if (!hasPermission(resource, action)) {
      return (
        <Box p={3}>
          <Alert severity="error">
            <Typography variant="h6" gutterBottom>
              Permisos Insuficientes
            </Typography>
            <Typography variant="body2">
              No tienes permisos para realizar esta acción.
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Tu rol actual: <strong>{user?.role}</strong>
            </Typography>
            <Typography variant="body2">
              Acción requerida: <strong>{action}</strong> en <strong>{resource}</strong>
            </Typography>
          </Alert>
        </Box>
      );
    }
  }

  // Si todo está bien, mostrar el contenido
  return children;
};

// Componente específico para rutas que requieren roles
export const RoleProtectedRoute = ({ children, roles, ...props }) => {
  return (
    <ProtectedRoute requiredRoles={roles} {...props}>
      {children}
    </ProtectedRoute>
  );
};

// Componente específico para rutas que requieren permisos
export const PermissionProtectedRoute = ({ children, resource, action, ...props }) => {
  return (
    <ProtectedRoute 
      requiredPermission={{ resource, action }} 
      {...props}
    >
      {children}
    </ProtectedRoute>
  );
};

export default ProtectedRoute;