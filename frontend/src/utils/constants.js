// Roles de usuario
export const USER_ROLES = {
  PRESIDENTE: 'PRESIDENTE',
  VOCAL: 'VOCAL',
  COORDINADOR: 'COORDINADOR',
  VOLUNTARIO: 'VOLUNTARIO',
};

// Etiquetas de roles para mostrar
export const ROLE_LABELS = {
  [USER_ROLES.PRESIDENTE]: 'Presidente',
  [USER_ROLES.VOCAL]: 'Vocal',
  [USER_ROLES.COORDINADOR]: 'Coordinador',
  [USER_ROLES.VOLUNTARIO]: 'Voluntario',
};

// Categorías de donaciones
export const DONATION_CATEGORIES = {
  ROPA: 'ROPA',
  ALIMENTOS: 'ALIMENTOS',
  JUGUETES: 'JUGUETES',
  UTILES_ESCOLARES: 'UTILES_ESCOLARES',
};

// Etiquetas de categorías para mostrar
export const CATEGORY_LABELS = {
  [DONATION_CATEGORIES.ROPA]: 'Ropa',
  [DONATION_CATEGORIES.ALIMENTOS]: 'Alimentos',
  [DONATION_CATEGORIES.JUGUETES]: 'Juguetes',
  [DONATION_CATEGORIES.UTILES_ESCOLARES]: 'Útiles Escolares',
};

// Estados de eventos
export const EVENT_STATUS = {
  UPCOMING: 'UPCOMING',
  ONGOING: 'ONGOING',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
};

// Configuración de la aplicación
export const APP_CONFIG = {
  NAME: 'ONG Empuje Comunitario',
  VERSION: '1.0.0',
  API_TIMEOUT: 10000,
  ITEMS_PER_PAGE: 10,
};

// Mensajes de error comunes
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Verifica tu conexión a internet.',
  UNAUTHORIZED: 'No tienes permisos para realizar esta acción.',
  NOT_FOUND: 'El recurso solicitado no fue encontrado.',
  SERVER_ERROR: 'Error interno del servidor. Intenta de nuevo más tarde.',
  VALIDATION_ERROR: 'Los datos ingresados no son válidos.',
};

// Mensajes de éxito
export const SUCCESS_MESSAGES = {
  USER_CREATED: 'Usuario creado exitosamente.',
  USER_UPDATED: 'Usuario actualizado exitosamente.',
  USER_DELETED: 'Usuario eliminado exitosamente.',
  DONATION_CREATED: 'Donación registrada exitosamente.',
  DONATION_UPDATED: 'Donación actualizada exitosamente.',
  DONATION_DELETED: 'Donación eliminada exitosamente.',
  EVENT_CREATED: 'Evento creado exitosamente.',
  EVENT_UPDATED: 'Evento actualizado exitosamente.',
  EVENT_DELETED: 'Evento eliminado exitosamente.',
  LOGIN_SUCCESS: 'Inicio de sesión exitoso.',
  LOGOUT_SUCCESS: 'Sesión cerrada exitosamente.',
};