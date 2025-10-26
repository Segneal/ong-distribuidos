import axios from 'axios';
import API_CONFIG, { getAuthHeaders, API_ENDPOINTS } from '../config/api';

// Crear instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.DEFAULT_HEADERS
});

// Interceptor para agregar token de autenticación automáticamente
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Manejar errores de autenticación
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Servicios de API
export const apiService = {
  // Métodos genéricos
  get: (url, config = {}) => apiClient.get(url, config),
  post: (url, data, config = {}) => apiClient.post(url, data, config),
  put: (url, data, config = {}) => apiClient.put(url, data, config),
  delete: (url, config = {}) => apiClient.delete(url, config),
  
  // Servicios específicos de filtros
  filters: {
    // Filtros de donaciones
    getDonationFilters: () => apiClient.get(API_ENDPOINTS.FILTERS.DONATIONS),
    saveDonationFilter: (data) => apiClient.post(API_ENDPOINTS.FILTERS.DONATIONS, data),
    updateDonationFilter: (id, data) => apiClient.put(`${API_ENDPOINTS.FILTERS.DONATIONS}/${id}`, data),
    deleteDonationFilter: (id) => apiClient.delete(`${API_ENDPOINTS.FILTERS.DONATIONS}/${id}`),
    
    // Filtros de eventos
    getEventFilters: () => apiClient.get(API_ENDPOINTS.FILTERS.EVENTS),
    saveEventFilter: (data) => apiClient.post(API_ENDPOINTS.FILTERS.EVENTS, data),
    updateEventFilter: (id, data) => apiClient.put(`${API_ENDPOINTS.FILTERS.EVENTS}/${id}`, data),
    deleteEventFilter: (id) => apiClient.delete(`${API_ENDPOINTS.FILTERS.EVENTS}/${id}`)
  },
  
  // Servicios de reportes
  reports: {
    // Exportar donaciones a Excel
    exportDonationsExcel: (filters) => apiClient.post(API_ENDPOINTS.REPORTS.EXCEL_EXPORT, { filtros: filters }),
    
    // Descargar archivo Excel
    downloadExcel: (downloadUrl) => apiClient.get(downloadUrl, { responseType: 'blob' })
  },
  
  // Servicios de consulta de red
  network: {
    consultation: (organizationIds) => apiClient.post(API_ENDPOINTS.NETWORK.CONSULTATION, { organizationIds })
  }
};

export default apiService;