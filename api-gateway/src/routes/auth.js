const express = require('express');
const { userService } = require('../services/grpcClients');
const { userTransformers, handleGrpcError, validateInput } = require('../utils/grpcMapper');
const authService = require('../services/authService');
const { authenticateToken } = require('../middleware/auth');
const router = express.Router();

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { usernameOrEmail, password } = req.body;

    // Validación básica
    if (!usernameOrEmail || !password) {
      return res.status(400).json({
        error: 'Usuario/email y contraseña son requeridos',
        timestamp: new Date().toISOString()
      });
    }

    // Validar formato de entrada
    if (typeof usernameOrEmail !== 'string' || typeof password !== 'string') {
      return res.status(400).json({
        error: 'Usuario/email y contraseña deben ser texto',
        timestamp: new Date().toISOString()
      });
    }

    // Transformar datos para gRPC
    const grpcRequest = userTransformers.toGrpcAuth({ usernameOrEmail, password });

    // Llamar al microservicio de usuarios
    const grpcResponse = await userService.authenticateUser(grpcRequest);

    // Transformar respuesta
    const response = userTransformers.fromGrpcUserResponse(grpcResponse);

    console.log('=== LOGIN DEBUG ===');
    console.log('gRPC Response user:', grpcResponse.user ? {
      id: grpcResponse.user.id,
      username: grpcResponse.user.username,
      organization: grpcResponse.user.organization
    } : 'No user');
    console.log('Transformed response user:', response.user ? {
      id: response.user.id,
      username: response.user.username,
      organization: response.user.organization
    } : 'No user');

    if (response.success) {
      // El token ya viene del microservicio, pero podemos generar uno nuevo si es necesario
      const token = response.token || authService.generateToken({
        user_id: response.user.id,
        username: response.user.username,
        role: response.user.role,
        organization: response.user.organization
      });

      res.status(200).json({
        success: true,
        message: response.message,
        user: {
          id: response.user.id,
          username: response.user.username,
          firstName: response.user.firstName,
          lastName: response.user.lastName,
          email: response.user.email,
          role: response.user.role,
          organization: response.user.organization,
          isActive: response.user.isActive
        },
        token: token,
        expiresIn: process.env.JWT_EXPIRES_IN || '24h',
        timestamp: new Date().toISOString()
      });
    } else {
      // Mapear mensajes de error específicos según los requisitos
      let statusCode = 401;
      let errorMessage = response.message;

      if (response.message === 'Usuario/email inexistente') {
        statusCode = 404;
        errorMessage = 'Usuario/email inexistente';
      } else if (response.message === 'Credenciales incorrectas') {
        statusCode = 401;
        errorMessage = 'Credenciales incorrectas';
      } else if (response.message === 'Usuario inactivo') {
        statusCode = 403;
        errorMessage = 'Usuario inactivo';
      }

      res.status(statusCode).json({
        error: errorMessage,
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    console.error('Error en login:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json({
      ...errorResponse.error,
      timestamp: new Date().toISOString()
    });
  }
});

// POST /api/auth/logout
router.post('/logout', authenticateToken, async (req, res) => {
  try {
    // Para logout básico, simplemente confirmamos la acción
    // En una implementación completa, aquí se invalidaría el token en una blacklist
    res.status(200).json({
      success: true,
      message: 'Sesión cerrada exitosamente',
      user: req.user.username,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error en logout:', error);
    res.status(500).json({
      error: 'Error interno del servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// GET /api/auth/me - Obtener información del usuario actual
router.get('/me', authenticateToken, async (req, res) => {
  try {
    res.status(200).json({
      success: true,
      user: {
        id: req.user.id,
        username: req.user.username,
        role: req.user.role
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error en /me:', error);
    res.status(500).json({
      error: 'Error interno del servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// POST /api/auth/verify - Verificar si un token es válido
router.post('/verify', async (req, res) => {
  try {
    const { token } = req.body;
    
    if (!token) {
      return res.status(400).json({
        error: 'Token requerido',
        timestamp: new Date().toISOString()
      });
    }

    const decoded = authService.verifyToken(token);
    
    res.status(200).json({
      success: true,
      valid: true,
      user: {
        id: decoded.user_id,
        username: decoded.username,
        role: decoded.role
      },
      expiresAt: new Date(decoded.exp * 1000).toISOString(),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(401).json({
      success: false,
      valid: false,
      error: 'Token inválido o expirado',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;