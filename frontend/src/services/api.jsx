import axios from 'axios';

// Normalize API base: prefer relative '/api' in dev to utilize Vite Proxy (handling HTTPS->HTTP)
function resolveApiBase() {
  // In development, ALWAYS use relative path to route through Vite Proxy (avoid Mixed Content)
  if (import.meta.env.DEV) {
    return '/api';
  }

  const envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl || envUrl === '') return '/api';
  return envUrl.replace(/\/$/, '');
}

export const API_BASE_URL = resolveApiBase();
export const API_ORIGIN = (() => {
  try {
    const u = new URL(API_BASE_URL, window.location.origin);
    return u.origin;
  } catch {
    return window.location.origin;
  }
})();

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for production stability
  headers: {}, // Removed default Content-Type: application/json
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Skip auth header for login and token refresh endpoints
    // (sending an expired token causes DRF to reject with 401 before the view runs)
    const url = config.url || '';
    const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/token/refresh');

    let token = null;

    if (!isAuthEndpoint) {
      // 1. Try sessionStorage first (Standard active memory block)
      const sessionAuth = sessionStorage.getItem('postventa_auth');
      if (sessionAuth) {
        try {
          const parsed = JSON.parse(sessionAuth);
          token = parsed.token || parsed.access_token || parsed.access;
        } catch (error) {
          sessionStorage.removeItem('postventa_auth');
        }
      }
      if (!token) {
        token = sessionStorage.getItem('access_token');
      }

      // 2. Try localStorage as last resort (Legacy/Persistent memory block)
      if (!token) {
        const localAuthRaw = localStorage.getItem('postventa_auth');
        if (localAuthRaw) {
          try {
            const parsed = JSON.parse(localAuthRaw);
            token = parsed.token || parsed.access_token || parsed.access;
          } catch (error) {
            localStorage.removeItem('postventa_auth');
          }
        }
      }
      if (!token) {
        token = localStorage.getItem('access_token');
      }

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    // NEW: Inject Country Context Header
    const countryCode = localStorage.getItem('country_code') || 'CL';
    config.headers['X-Country-Code'] = countryCode;

    if (!token && !isAuthEndpoint) {
      // Solo mostrar advertencia para rutas que requieren autenticación
      const authRoutes = ['/incidents/', '/users/', '/documents/', '/reports/', '/notifications/'];
      const needsAuth = authRoutes.some(route => config.url?.includes(route));
      if (needsAuth) {
        console.warn('No token available for request to:', config.url);
      }
    }

    // Log request details
    // Optional debug logs can be enabled via VITE_DEBUG_HTTP
    const debug = import.meta.env.VITE_DEBUG_HTTP === 'true';
    if (debug) {
      // Keep minimal, non-sensitive logs
      console.debug('[HTTP]', config.method?.toUpperCase(), config.url, token ? '🔑' : '❌');
    }

    // Establecer Content-Type: application/json por defecto si NO es FormData
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    } else {
      // Si es FormData, nos aseguramos de que no haya Content-Type previo
      // para que Axios/Navegador pongan el multipart/form-data con boundary correcto
      if (typeof config.headers.delete === 'function') {
        config.headers.delete('Content-Type');
      } else {
        delete config.headers['Content-Type'];
      }
      config.headers['Content-Type'] = undefined;

      if (debug) {
        console.debug('[HTTP] FormData detected, Content-Type removed to allow auto-boundary', config.headers);
      }
    }

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    const debug = import.meta.env.VITE_DEBUG_HTTP === 'true';
    if (debug) {
      console.debug('[HTTP OK]', response.status, response.config?.url);
    }
    return response;
  },
  async (error) => {
    const debug = import.meta.env.VITE_DEBUG_HTTP === 'true';
    if (debug) {
      console.debug('[HTTP ERR]', error.response?.status, error.config?.url);
    }

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      const url = originalRequest.url || '';
      // Don't try to refresh token if the error comes from the login endpoint itself
      // Check for both relative and absolute paths, and specific login endpoint
      if (url.includes('/login') || url.includes('token/refresh')) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      console.warn('🔄 Token expirado, intentando refresh...');

      // Cleanup de caches huérfanos antes del refresh de seguridad
      localStorage.removeItem('postventa_auth');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;

          // Update both storage methods
          localStorage.setItem('access_token', access);

          // Update the auth storage as well
          const authData = localStorage.getItem('postventa_auth');
          if (authData) {
            try {
              const parsed = JSON.parse(authData);
              parsed.token = access;
              localStorage.setItem('postventa_auth', JSON.stringify(parsed));
            } catch (error) {
              console.warn('Error updating auth data:', error);
            }
          }

          api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
          originalRequest.headers['Authorization'] = `Bearer ${access}`;

          return api(originalRequest);
        } else {
          console.warn('❌ No refresh token available');
          throw new Error('No refresh token');
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
        // Clear all persistent & volatile auth data
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('postventa_auth');
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        sessionStorage.removeItem('postventa_auth');
        sessionStorage.removeItem('app_initialized');
        delete api.defaults.headers.common['Authorization'];

        // Dispatch logout event instead of reloading
        window.dispatchEvent(new Event('auth:logout'));
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('auth/login/', credentials),
  logout: (refreshToken) => api.post('auth/logout/', { refresh_token: refreshToken }),
  me: () => api.get('auth/me/'),
  changePassword: (data) => api.put('auth/change-password/', data),
  refreshToken: (refreshToken) => api.post('auth/token/refresh/', { refresh: refreshToken }),
};

export const incidentsAPI = {
  list: (params) => api.get('/incidents/', { params }),
  create: (data) => api.post('/incidents/', data),
  get: (id) => api.get(`/incidents/${id}/`),
  update: (id, data) => api.patch(`/incidents/${id}/`, data),
  delete: (id) => api.delete(`/incidents/${id}/`),
  debug: () => api.get('/incidents/'), // Use regular endpoint for debug
  uploadImage: (incidentId, image) => {
    const formData = new FormData();
    formData.append('image', image);
    return api.post(`/incidents/${incidentId}/images/`, formData);
  },
  analyzeImage: (imageId) => api.post(`/incidents/images/${imageId}/analyze/`),
  updateStatus: (incidentId, data) => api.post(`/incidents/${incidentId}/status/`, data),
  close: (incidentId, data) => api.post(`/incidents/${incidentId}/close/`, data),
  reopen: (incidentId) => api.post(`/incidents/${incidentId}/reopen/`),
  dashboard: (params) => api.get('/incidents/dashboard/', { params }),
  uploadAttachment: (incidentId, formData) => api.post(`/documents/incident-attachments/${incidentId}/upload/`, formData),
  fixEscalation: (incidentId) => api.post(`/incidents/${incidentId}/fix-escalation/`),
  export: (params) => api.get('/incidents/export/', { params, responseType: 'blob' }),
};

export const documentsAPI = {
  list: (params) => api.get('/documents/', { params }),
  getByIncidents: (params) => api.get('/documents/by-incidents/', { params }),
  create: (data) => api.post('/documents/', data),
  get: (id) => api.get(`/documents/${id}/`),
  update: (id, data) => api.put(`/documents/${id}/`, data),
  delete: (id) => api.delete(`/documents/${id}/`),
  generate: (data) => api.post('/documents/generate/', data),
  generateForIncident: (incidentId, data) => api.post(`/documents/generate/${incidentId}/`, data),
  edit: (documentId, data) => api.post(`/documents/${documentId}/edit/`, data),
  convert: (documentId, data) => api.post(`/documents/${documentId}/convert/`, data),
  versions: (documentId) => api.get(`/documents/${documentId}/versions/`),
  conversions: (documentId) => api.get(`/documents/${documentId}/conversions/`),
  search: (params) => api.get('/documents/search/', { params }),
  dashboard: () => api.get('/documents/dashboard/'),
};

export const templatesAPI = {
  list: () => api.get('/documents/templates/'),
  create: (data) => api.post('/documents/templates/', data),
  get: (id) => api.get(`/documents/templates/${id}/`),
  update: (id, data) => api.put(`/documents/templates/${id}/`, data),
  delete: (id) => api.delete(`/documents/templates/${id}/`),
};

export const aiAPI = {
  analyzeImage: (image) => {
    const formData = new FormData();
    formData.append('image', image);
    return api.post('/ai/analyze-image/', formData);
  },
  generateReport: (data) => api.post('/ai/generate-report/', data),
  generateText: (data) => api.post('/ai/generate-text/', data),
  analyzeCause: (data) => api.post('/ai/generate-text/', {
    ...data,
    prompt_type: 'quality_analysis' // Indicador para el backend si es necesario
  }),
  providerStatus: () => api.get('/ai/providers/status/'),
  resetQuotas: () => api.post('/ai/providers/reset-quotas/'),
  analyzeClosure: (data) => api.post('/ai/writing/analyze-closure/', data),
  analysisHistory: () => api.get('/ai/analyses/'),
};

// NEW: AI Agents API - Advanced multi-step reasoning agents
export const aiAgentsAPI = {
  // Main agent query endpoint - sends query and gets intelligent response
  query: (queryData) => api.post('/ai-agents/query/', queryData),

  // Analyze image(s) with agent (multi-step reasoning with context)
  analyzeImage: (input, query = 'Analiza esta imagen técnicamente', provider = null) => {
    const formData = new FormData();
    formData.append('query', query);
    if (provider) formData.append('provider', provider);

    if (Array.isArray(input)) {
      input.forEach(file => formData.append('image', file)); // Use 'image' to match backend analyze_real_image expectation or 'images' if handled as list
    } else {
      formData.append('image', input);
    }

    return api.post('/ai-agents/analyze-image/', formData);
  },

  // Generate professional report
  generateReport: (data) => api.post('/ai-agents/generate-report/', data),

  // Get agent system status
  status: () => api.get('/ai-agents/status/'),
};

export const usersAPI = {
  list: (params) => api.get('/users/', { params }),
  create: (data) => api.post('/users/', data),
  get: (id) => api.get(`/users/${id}/`),
  update: (id, data) => {
    // Check if data is FormData (for file uploads like digital_signature)
    if (data instanceof FormData) {
      return api.put(`/users/${id}/`, data);
    }
    return api.put(`/users/${id}/`, data);
  },
  delete: (id) => api.delete(`/users/${id}/`),
  stats: () => api.get('/users/stats/'),
  toggleStatus: (id) => api.post(`/users/${id}/toggle-status/`),
  resetPassword: (id, data) => api.post(`/users/${id}/reset-password/`, data),
  changePassword: (id, data) => api.post(`/users/${id}/reset-password/`, data), // Alias for compatibility
  changeOwnPassword: (data) => api.post('/users/change-password/', data),
  getPermissions: () => api.get('/users/permissions/'),
};

export const auditAPI = {
  logs: (params) => api.get('/audit/logs/', { params }),
  actionChoices: () => api.get('/audit/action-choices/'),
  export: (data) => api.post('/audit/logs/export/', data, { responseType: 'blob' }),
};

// Document Traceability APIs
export const visitReportsAPI = {
  list: (params) => api.get('/documents/visit-reports/', { params }),
  create: (data) => api.post('/documents/visit-reports/', data),
  get: (id) => api.get(`/documents/visit-reports/${id}/`),
  update: (id, data) => api.patch(`/documents/visit-reports/${id}/`, data),  // Changed to PATCH for partial updates
  delete: (id) => api.delete(`/documents/visit-reports/${id}/`),
  generateOrderNumber: () => api.get('/documents/generate-order-number/'),
};


export const supplierReportsAPI = {
  list: (params) => api.get('/documents/supplier-reports/', { params }),
  create: (data) => api.post('/documents/supplier-reports/', data),
  get: (id) => api.get(`/documents/supplier-reports/${id}/`),
  update: (id, data) => api.put(`/documents/supplier-reports/${id}/`, data),
  delete: (id) => api.delete(`/documents/supplier-reports/${id}/`),
};

export const qualityReportsAPI = {
  list: (params) => api.get('/documents/quality-reports/', { params }),
  create: (data) => api.post('/documents/quality-reports/', data),
  get: (id) => api.get(`/documents/quality-reports/${id}/`),
  update: (id, data) => api.put(`/documents/quality-reports/${id}/`, data),
  delete: (id) => api.delete(`/documents/quality-reports/${id}/`),
  generatePDF: (id) => api.post(`/documents/quality-reports/${id}/generate/`),
};

// Extended documents API with new methods
documentsAPI.createVisitReport = (data) => api.post('/documents/visit-reports/', data);
documentsAPI.createSupplierReport = (data) => api.post('/documents/supplier-reports/', data);

// Dashboard API
export const dashboardAPI = {
  getMetrics: () => api.get('/dashboard/metrics/'),
};

// Notifications API (HTTP fallback when WebSocket is disabled)
export const notificationsAPI = {
  list: (params) => api.get('/notifications/notifications/', { params }),
  recent: () => api.get('/notifications/notifications/recent/'),
  unreadCount: () => api.get('/notifications/notifications/unread_count/'),
  markAsRead: (id) => api.post(`/notifications/notifications/${id}/mark_read/`),
  markAllAsRead: () => api.post('/notifications/notifications/mark_all_read/'),
  important: () => api.get('/notifications/notifications/important/'),
};

export default api;

