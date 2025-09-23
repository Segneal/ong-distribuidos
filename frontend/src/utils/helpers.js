import { ROLE_LABELS, CATEGORY_LABELS } from './constants';

// Formatear fecha para mostrar
export const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Formatear fecha solo (sin hora)
export const formatDateOnly = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

// Obtener etiqueta de rol
export const getRoleLabel = (role) => {
  return ROLE_LABELS[role] || role;
};

// Obtener etiqueta de categoría
export const getCategoryLabel = (category) => {
  return CATEGORY_LABELS[category] || category;
};

// Validar email
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validar teléfono (formato básico)
export const isValidPhone = (phone) => {
  const phoneRegex = /^[\d\s\-\+\(\)]+$/;
  return phoneRegex.test(phone) && phone.length >= 8;
};

// Capitalizar primera letra
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

// Truncar texto
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Obtener iniciales de nombre
export const getInitials = (firstName, lastName) => {
  const first = firstName ? firstName.charAt(0).toUpperCase() : '';
  const last = lastName ? lastName.charAt(0).toUpperCase() : '';
  return first + last;
};

// Verificar si una fecha es futura
export const isFutureDate = (dateString) => {
  if (!dateString) return false;
  const date = new Date(dateString);
  const now = new Date();
  return date > now;
};

// Verificar si una fecha es pasada
export const isPastDate = (dateString) => {
  if (!dateString) return false;
  const date = new Date(dateString);
  const now = new Date();
  return date < now;
};

// Formatear número con separadores de miles
export const formatNumber = (number) => {
  if (typeof number !== 'number') return '0';
  return number.toLocaleString('es-ES');
};

// Manejar errores de API
export const handleApiError = (error) => {
  if (error.response) {
    // Error de respuesta del servidor
    return error.response.data?.message || error.response.data?.error || 'Error del servidor';
  } else if (error.request) {
    // Error de red
    return 'Error de conexión. Verifica tu conexión a internet.';
  } else {
    // Otro tipo de error
    return error.message || 'Error desconocido';
  }
};

// Generar ID único simple
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// Debounce function para búsquedas
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};