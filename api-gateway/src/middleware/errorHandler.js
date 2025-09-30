/**
 * Middleware de manejo de errores centralizado
 */
const errorHandler = (err, req, res, next) => {
  console.error('Error capturado por middleware:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    user: req.user?.username || 'No autenticado',
    timestamp: new Date().toISOString()
  });

  // Error de validación de JWT
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: 'Token de acceso inválido',
      message: 'El token proporcionado no es válido',
      timestamp: new Date().toISOString()
    });
  }

  // Token expirado
  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      error: 'Token expirado',
      message: 'El token de acceso ha expirado',
      timestamp: new Date().toISOString()
    });
  }

  // Error de autorización personalizado
  if (err.name === 'AuthorizationError') {
    return res.status(403).json({
      error: 'Acceso denegado',
      message: err.message,
      userRole: req.user?.role,
      timestamp: new Date().toISOString()
    });
  }

  // Error de validación de entrada
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Datos de entrada inválidos',
      message: err.message,
      details: err.details || [],
      timestamp: new Date().toISOString()
    });
  }

  // Error de gRPC
  if (err.code && typeof err.code === 'number') {
    const grpcToHttpStatus = {
      1: 499, // CANCELLED
      2: 500, // UNKNOWN
      3: 400, // INVALID_ARGUMENT
      4: 504, // DEADLINE_EXCEEDED
      5: 404, // NOT_FOUND
      6: 409, // ALREADY_EXISTS
      7: 403, // PERMISSION_DENIED
      8: 429, // RESOURCE_EXHAUSTED
      9: 400, // FAILED_PRECONDITION
      10: 409, // ABORTED
      11: 400, // OUT_OF_RANGE
      12: 501, // UNIMPLEMENTED
      13: 500, // INTERNAL
      14: 503, // UNAVAILABLE
      15: 500, // DATA_LOSS
      16: 401, // UNAUTHENTICATED
    };

    const httpStatus = grpcToHttpStatus[err.code] || 500;
    return res.status(httpStatus).json({
      error: 'Error del microservicio',
      message: err.details || err.message || 'Error interno del servidor',
      grpcCode: err.code,
      timestamp: new Date().toISOString()
    });
  }

  // Error genérico del servidor
  const status = err.status || err.statusCode || 500;
  res.status(status).json({
    error: status >= 500 ? 'Error interno del servidor' : err.message,
    message: status >= 500 ? 'Ha ocurrido un error inesperado' : err.message,
    timestamp: new Date().toISOString(),
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

/**
 * Middleware para manejar rutas no encontradas
 */
const notFoundHandler = (req, res) => {
  console.log({
    error: 'Ruta no encontrada',
    message: `La ruta ${req.method} ${req.originalUrl} no existe`,
    timestamp: new Date().toISOString()
  })
  res.status(404).json({
    error: 'Ruta no encontrada',
    message: `La ruta ${req.method} ${req.originalUrl} no existe`,
    timestamp: new Date().toISOString()
  });
};



/**
 * Función helper para crear errores de autorización
 */
const createAuthorizationError = (message, details = {}) => {
  const error = new Error(message);
  error.name = 'AuthorizationError';
  error.details = details;
  return error;
};

/**
 * Función helper para crear errores de validación
 */
const createValidationError = (message, details = []) => {
  const error = new Error(message);
  error.name = 'ValidationError';
  error.details = details;
  return error;
};

module.exports = {
  errorHandler,
  notFoundHandler,
  createAuthorizationError,
  createValidationError
};