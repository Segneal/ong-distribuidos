const jwt = require('jsonwebtoken');

class AuthService {
  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'your-secret-key';
    this.jwtExpiresIn = process.env.JWT_EXPIRES_IN || '24h';
  }

  /**
   * Genera un JWT token
   */
  generateToken(payload) {
    return jwt.sign(payload, this.jwtSecret, { 
      expiresIn: this.jwtExpiresIn,
      algorithm: 'HS256'
    });
  }

  /**
   * Verifica un JWT token
   */
  verifyToken(token) {
    try {
      return jwt.verify(token, this.jwtSecret);
    } catch (error) {
      throw new Error('Token inválido');
    }
  }

  /**
   * Extrae el token del header Authorization
   */
  extractTokenFromHeader(authHeader) {
    if (!authHeader) {
      throw new Error('Header de autorización requerido');
    }

    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0] !== 'Bearer') {
      throw new Error('Formato de token inválido');
    }

    return parts[1];
  }

  /**
   * Verifica si un usuario tiene el rol requerido
   */
  hasRole(userRole, requiredRoles) {
    if (!Array.isArray(requiredRoles)) {
      requiredRoles = [requiredRoles];
    }
    return requiredRoles.includes(userRole);
  }

  /**
   * Verifica permisos según el rol
   */
  checkPermissions(userRole, resource, action) {
    const permissions = {
      PRESIDENTE: {
        users: ['create', 'read', 'update', 'delete'],
        inventory: ['create', 'read', 'update', 'delete'],
        events: ['create', 'read', 'update', 'delete']
      },
      VOCAL: {
        inventory: ['create', 'read', 'update', 'delete']
      },
      COORDINADOR: {
        events: ['create', 'read', 'update', 'delete']
      },
      VOLUNTARIO: {
        events: ['read', 'participate']
      }
    };

    const userPermissions = permissions[userRole];
    if (!userPermissions) {
      return false;
    }

    const resourcePermissions = userPermissions[resource];
    if (!resourcePermissions) {
      return false;
    }

    return resourcePermissions.includes(action);
  }
}

module.exports = new AuthService();