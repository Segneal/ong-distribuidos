import axios from 'axios';

// Configuración base de Axios
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

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
  getUsers: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.includeInactive) {
      queryParams.append('includeInactive', 'true');
    }
    const queryString = queryParams.toString();
    return api.get(`/users${queryString ? `?${queryString}` : ''}`);
  },
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
  getEvents: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.includePastEvents) {
      queryParams.append('includePastEvents', 'true');
    }
    const queryString = queryParams.toString();
    return api.get(`/events${queryString ? `?${queryString}` : ''}`);
  },
  createEvent: (eventData) => api.post('/events', eventData),
  updateEvent: (id, eventData) => api.put(`/events/${id}`, eventData),
  deleteEvent: (id) => api.delete(`/events/${id}`),
  getEvent: (id) => api.get(`/events/${id}`),
  addParticipant: (eventId, userId) => api.post(`/events/${eventId}/participants`, { userId }),
  removeParticipant: (eventId, userId) => api.delete(`/events/${eventId}/participants/${userId}`),
  getParticipants: (eventId) => api.get(`/events/${eventId}/participants`),
  registerDistributedDonations: (eventId, donations) => api.post(`/events/${eventId}/distributed-donations`, { donations }),
  getDistributedDonations: (eventId) => api.get(`/events/${eventId}/distributed-donations`),
};

export const emailService = {
  sendWelcomeEmail: (emailData) => api.post('/email/welcome', emailData),
  testEmailConfig: () => api.get('/email/test'),
};

export const messagingService = {
  // Donation requests
  createDonationRequest: (requestData) => api.post('/messaging/create-donation-request', requestData),
  getExternalRequests: (params = {}) => api.post('/messaging/external-requests', params),
  cancelDonationRequest: (requestId) => api.post('/messaging/cancel-donation-request', { requestId }),
  getActiveRequests: () => api.post('/messaging/active-requests'),
  
  // Donation transfers
  transferDonations: (transferData) => api.post('/messaging/transfer-donations', transferData),
  getTransferHistory: (params = {}) => api.post('/messaging/transfer-history', params),
  
  // Donation offers
  createDonationOffer: (offerData) => api.post('/messaging/create-donation-offer', offerData),
  getExternalOffers: (params = {}) => api.post('/messaging/external-offers', params),
  
  // Events
  publishEvent: (eventData) => api.post('/messaging/publish-event', eventData),
  getExternalEvents: (params = {}) => api.post('/messaging/external-events', params),
  cancelEvent: (eventId) => api.post('/messaging/cancel-event', { eventId }),
  toggleEventExposure: (exposureData) => api.post('/messaging/toggle-event-exposure', exposureData),
  
  // Event adhesions
  createEventAdhesion: (adhesionData) => api.post('/messaging/create-event-adhesion', adhesionData),
  getVolunteerAdhesions: () => api.post('/messaging/volunteer-adhesions'),
  getEventAdhesions: (eventId) => api.post('/messaging/event-adhesions', { eventId }),
  approveEventAdhesion: (adhesionId) => api.post('/messaging/approve-event-adhesion', { adhesionId }),
  rejectEventAdhesion: (adhesionId, reason) => api.post('/messaging/reject-event-adhesion', { adhesionId, reason }),
};

// Servicio para health check
export const healthService = {
  check: () => api.get('/health', { baseURL: 'http://localhost:3001' }),
};

export default api;