const authService = require('../services/authService');

/**
 * Middleware para verificar JWT tokens
 */
const authenticateToken = (req, res, next) => {
  try {
    console.log(`authenticateToken - Method: ${req.method}, Path: ${req.path}`);
    console.log(`authenticateToken - Authorization header:`, req.headers.authorization);
    
    const token = authService.extractTokenFromHeader(req.headers.authorization);
    console.log(`authenticateToken - Extracted token:`, token ? 'Present' : 'Missing');
    
    const decoded = authService.verifyToken(token);
    console.log(`authenticateToken - Decoded token:`, decoded);
    
    // Agregar información del usuario al request
    req.user = {
      id: decoded.user_id,
      username: decoded.username,
      role: decoded.role
    };
    
    console.log(`authenticateToken - User set:`, req.user);
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
    console.log(`requireRole middleware - Method: ${req.method}, Path: ${req.path}`);
    console.log(`requireRole middleware - User:`, req.user);
    console.log(`requireRole middleware - Required roles:`, roles);
    
    if (!req.user) {
      console.log('requireRole middleware - No user found');
      return res.status(401).json({
        error: 'Usuario no autenticado',
        timestamp: new Date().toISOString()
      });
    }

    if (!authService.hasRole(req.user.role, roles)) {
      console.log(`requireRole middleware - Role check failed. User role: ${req.user.role}, Required: ${roles}`);
      return res.status(403).json({
        error: 'Permisos insuficientes',
        message: `Se requiere uno de los siguientes roles: ${Array.isArray(roles) ? roles.join(', ') : roles}`,
        userRole: req.user.role,
        timestamp: new Date().toISOString()
      });
    }

    console.log('requireRole middleware - Role check passed, proceeding to next middleware');
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