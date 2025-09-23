// Middleware para manejo centralizado de errores gRPC
const { handleGrpcError } = require('./grpcMapper');

const grpcErrorHandler = (error, req, res, next) => {
  // Si es un error gRPC, usar el handler específico
  if (error.code && typeof error.code === 'number') {
    const errorResponse = handleGrpcError(error);
    return res.status(errorResponse.status).json(errorResponse.error);
  }

  // Si no es un error gRPC, pasar al siguiente middleware de error
  next(error);
};

// Función helper para envolver rutas con manejo de errores gRPC
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch((error) => {
      grpcErrorHandler(error, req, res, next);
    });
  };
};

// Función para verificar conectividad básica con timeout
const checkGrpcConnection = async (client, serviceName, timeout = 5000) => {
  return new Promise((resolve) => {
    const deadline = new Date(Date.now() + timeout);
    
    // Intentar verificar el estado del canal
    const state = client.getChannel().getConnectivityState(true);
    
    if (state === 2) { // READY
      resolve({
        service: serviceName,
        status: 'connected',
        state: 'READY'
      });
    } else {
      resolve({
        service: serviceName,
        status: 'disconnected',
        state: getStateString(state)
      });
    }
  });
};

// Helper para convertir estado numérico a string
const getStateString = (state) => {
  const states = {
    0: 'IDLE',
    1: 'CONNECTING',
    2: 'READY',
    3: 'TRANSIENT_FAILURE',
    4: 'SHUTDOWN'
  };
  return states[state] || 'UNKNOWN';
};

// Función para crear respuesta de error estándar
const createErrorResponse = (message, code = 'INTERNAL_ERROR', details = null) => {
  return {
    error: message,
    code,
    details,
    timestamp: new Date().toISOString()
  };
};

// Función para crear respuesta de éxito estándar
const createSuccessResponse = (data, message = 'Operación exitosa') => {
  return {
    success: true,
    message,
    data,
    timestamp: new Date().toISOString()
  };
};

module.exports = {
  grpcErrorHandler,
  asyncHandler,
  checkGrpcConnection,
  createErrorResponse,
  createSuccessResponse,
};