// Configuración de la API
const API_CONFIG = {
  // URL base del API Gateway
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:3001',
  
  // Timeout por defecto
  TIMEOUT: 30000,
  
  // Headers por defecto
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  }
};

// Función para obtener el token de autenticación
export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// Función para obtener headers con autenticación
export const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    ...API_CONFIG.DEFAULT_HEADERS,
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// URLs de endpoints
export const API_ENDPOINTS = {
  // Autenticación
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    PROFILE: '/api/auth/profile'
  },
  
  // Reportes
  REPORTS: {
    DONATIONS: '/api/reports/donations',
    EVENTS: '/api/reports/events',
    EXCEL_EXPORT: '/api/reports/donations/excel'
  },
  
  // Filtros
  FILTERS: {
    DONATIONS: '/api/filters/donations',
    EVENTS: '/api/filters/events'
  },
  
  // Consulta de red
  NETWORK: {
    CONSULTATION: '/api/network/consultation'
  },
  
  // GraphQL
  GRAPHQL: '/api/graphql'
};

export default API_CONFIG;