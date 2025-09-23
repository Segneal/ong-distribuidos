const authService = require('../services/authService');

/**
 * Middleware para verificar JWT tokens
 */
const authenticateToken = (req, res, next) => {
  try {
    const token = authService.extractTokenFromHeader(req.headers.authorization);
    const decoded = authService.verifyToken(token);
    
    // Agregar información del usuario al request
    req.user = {
      id: decoded.user_id,
      username: decoded.username,
      role: decoded.role
    };
    
    next();
  } catch (error) {
    console.error('Error de autenticación:', error.message);
    return res.status(401).json({
      error: 'Token de acceso inválido',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
};

/**
 * Middleware para verificar roles específicos
 */
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Usuario no autenticado',
        timestamp: new Date().toISOString()
      });
    }

    if (!authService.hasRole(req.user.role, roles)) {
      return res.status(403).json({
        error: 'Permisos insuficientes',
        message: `Se requiere uno de los siguientes roles: ${Array.isArray(roles) ? roles.join(', ') : roles}`,
        userRole: req.user.role,
        timestamp: new Date().toISOString()
      });
    }

    next();
  };
};

/**
 * Middleware para verificar permisos específicos
 */
const requirePermission = (resource, action) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Usuario no autenticado',
        timestamp: new Date().toISOString()
      });
    }

    if (!authService.checkPermissions(req.user.role, resource, action)) {
      return res.status(403).json({
        error: 'Permisos insuficientes',
        message: `No tienes permisos para ${action} en ${resource}`,
        userRole: req.user.role,
        timestamp: new Date().toISOString()
      });
    }

    next();
  };
};

/**
 * Middleware opcional de autenticación (no falla si no hay token)
 */
const optionalAuth = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (authHeader) {
      const token = authService.extractTokenFromHeader(authHeader);
      const decoded = authService.verifyToken(token);
      
      req.user = {
        id: decoded.user_id,
        username: decoded.username,
        role: decoded.role
      };
    }
  } catch (error) {
    // No hacer nada, continuar sin usuario autenticado
    console.log('Token opcional inválido:', error.message);
  }
  
  next();
};

module.exports = {
  authenticateToken,
  requireRole,
  requirePermission,
  optionalAuth
};