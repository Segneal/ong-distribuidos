import axios from 'axios';

// Configuración base de Axios
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requests - agregar token de autenticación
api.interceptors.request.use(
  (config) => {
    // TODO: Implementar cuando se tenga autenticación
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para responses - manejo de errores
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Manejo básico de errores
    if (error.response?.status === 401) {
      // Token expirado o no válido
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Servicios de API
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  verify: (tokenData) => api.post('/auth/verify', tokenData),
  me: () => api.get('/auth/me'),
};

export const usersService = {
  getUsers: () => api.get('/users'),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (id, userData) => api.put(`/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/users/${id}`),
  getUser: (id) => api.get(`/users/${id}`),
};

export const inventoryService = {
  getDonations: () => api.get('/inventory'),
  createDonation: (donationData) => api.post('/inventory', donationData),
  updateDonation: (id, donationData) => api.put(`/inventory/${id}`, donationData),
  deleteDonation: (id) => api.delete(`/inventory/${id}`),
  getDonation: (id) => api.get(`/inventory/${id}`),
};

export const eventsService = {
  getEvents: () => api.get('/events'),
  createEvent: (eventData) => api.post('/events', eventData),
  updateEvent: (id, eventData) => api.put(`/events/${id}`, eventData),
  deleteEvent: (id) => api.delete(`/events/${id}`),
  getEvent: (id) => api.get(`/events/${id}`),
  addParticipant: (eventId, userId) => api.post(`/events/${eventId}/participants`, { userId }),
  removeParticipant: (eventId, userId) => api.delete(`/events/${eventId}/participants/${userId}`),
};

// Servicio para health check
export const healthService = {
  check: () => api.get('/health', { baseURL: 'http://localhost:3000' }),
};

export default api;