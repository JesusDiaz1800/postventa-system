import axios from 'axios';

// Normalize API base: prefer relative '/api' in dev; if an absolute URL is provided
// and it is https://localhost, force http to avoid dev server HTTPS errors.
function resolveApiBase() {
  const envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl || envUrl === '') return '/api';
  try {
    const u = new URL(envUrl, window.location.origin);
    if ((u.hostname === 'localhost' || u.hostname === '127.0.0.1') && u.protocol === 'https:') {
      u.protocol = 'http:';
      return u.pathname.endsWith('/api') ? u.toString().replace(/\/$/, '') : u.toString().replace(/\/$/, '') + '/api';
    }
    return envUrl.replace(/\/$/, '');
  } catch {
    return '/api';
  }
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
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
<<<<<<< HEAD
    // Try to get token from the auth storage
    const authData = localStorage.getItem('postventa_auth');
    let token = null;
    
    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        token = parsed.token;
      } catch (error) {
        console.warn('Error parsing auth data:', error);
      }
    }
    
    // Fallback to access_token for backward compatibility
=======
    // Try to get token from multiple sources
    let token = null;
    
    // 1. Try postventa_auth
    const authData = localStorage.getItem('postventa_auth');
    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        token = parsed.token || parsed.access_token || parsed.access;
      } catch (error) {
        console.warn('Error parsing auth data:', error);
        // Limpiar datos corruptos
        localStorage.removeItem('postventa_auth');
      }
    }
    
    // 2. Fallback to access_token for backward compatibility
>>>>>>> 674c244 (tus cambios)
    if (!token) {
      token = localStorage.getItem('access_token');
    }
    
<<<<<<< HEAD
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
=======
    // 3. Try sessionStorage as last resort
    if (!token) {
      token = sessionStorage.getItem('access_token');
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      // Solo mostrar advertencia para rutas que requieren autenticación
      const authRoutes = ['/incidents/', '/users/', '/documents/', '/reports/', '/notifications/'];
      const needsAuth = authRoutes.some(route => config.url?.includes(route));
      if (needsAuth) {
        console.warn('No token available for request to:', config.url);
      }
>>>>>>> 674c244 (tus cambios)
    }
    
    // Log request details
    // Optional debug logs can be enabled via VITE_DEBUG_HTTP
    const debug = import.meta.env.VITE_DEBUG_HTTP === 'true';
    if (debug) {
      // Keep minimal, non-sensitive logs
<<<<<<< HEAD
      console.debug('[HTTP]', config.method?.toUpperCase(), config.url);
=======
      console.debug('[HTTP]', config.method?.toUpperCase(), config.url, token ? '🔑' : '❌');
>>>>>>> 674c244 (tus cambios)
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
      originalRequest._retry = true;
<<<<<<< HEAD
=======
      console.warn('🔄 Token expirado, intentando refresh...');
>>>>>>> 674c244 (tus cambios)

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
<<<<<<< HEAD
=======
          console.log('🔄 Refrescando token...');
>>>>>>> 674c244 (tus cambios)
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

<<<<<<< HEAD
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
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('postventa_auth');
        delete api.defaults.headers.common['Authorization'];
        window.location.href = '/login';
=======
          const { access } = response.data;
          console.log('✅ Token refrescado exitosamente');
          
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
        // Clear all auth data and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('postventa_auth');
        sessionStorage.removeItem('app_initialized');
        delete api.defaults.headers.common['Authorization'];
        
        console.log('🔄 Limpiando datos y recargando página...');
        // Force page reload to reset React state
        setTimeout(() => {
          window.location.reload();
        }, 1000);
>>>>>>> 674c244 (tus cambios)
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
<<<<<<< HEAD
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  me: () => api.get('/auth/me/'),
  changePassword: (data) => api.put('/auth/change-password/', data),
  refreshToken: (refreshToken) => api.post('/auth/token/refresh/', { refresh: refreshToken }),
=======
  login: (credentials) => api.post('auth/login/', credentials),
  logout: (refreshToken) => api.post('auth/logout/', { refresh_token: refreshToken }),
  me: () => api.get('auth/me/'),
  changePassword: (data) => api.put('auth/change-password/', data),
  refreshToken: (refreshToken) => api.post('auth/token/refresh/', { refresh: refreshToken }),
>>>>>>> 674c244 (tus cambios)
};

export const incidentsAPI = {
  list: (params) => api.get('/incidents/', { params }),
  create: (data) => api.post('/incidents/', data),
  get: (id) => api.get(`/incidents/${id}/`),
  update: (id, data) => api.put(`/incidents/${id}/`, data),
  delete: (id) => api.delete(`/incidents/${id}/`),
  debug: () => api.get('/incidents/'), // Use regular endpoint for debug
  uploadImage: (incidentId, image) => {
    const formData = new FormData();
    formData.append('image', image);
    return api.post(`/incidents/${incidentId}/images/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  analyzeImage: (imageId) => api.post(`/incidents/images/${imageId}/analyze/`),
  updateStatus: (incidentId, data) => api.post(`/incidents/${incidentId}/status/`, data),
  close: (incidentId, data) => api.post(`/incidents/${incidentId}/close/`, data),
  reopen: (incidentId) => api.post(`/incidents/${incidentId}/reopen/`),
  createLabReport: (incidentId, data) => api.post(`/incidents/${incidentId}/lab-reports/`, data),
  dashboard: () => api.get('/incidents/dashboard/'),
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
    return api.post('/ai/analyze-image/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  generateReport: (data) => api.post('/ai/generate-report/', data),
  generateText: (data) => api.post('/ai/generate-text/', data),
  providerStatus: () => api.get('/ai/providers/status/'),
  resetQuotas: () => api.post('/ai/providers/reset-quotas/'),
  analysisHistory: () => api.get('/ai/analyses/'),
};

export const usersAPI = {
  list: (params) => api.get('/users/', { params }),
  create: (data) => api.post('/users/', data),
  get: (id) => api.get(`/users/${id}/`),
  update: (id, data) => api.put(`/users/${id}/`, data),
  delete: (id) => api.delete(`/users/${id}/`),
  stats: () => api.get('/users/stats/'),
  toggleStatus: (id) => api.post(`/users/${id}/toggle-status/`),
  resetPassword: (id, data) => api.post(`/users/${id}/reset-password/`, data),
  changeOwnPassword: (data) => api.post('/users/change-password/', data),
  getPermissions: () => api.get('/users/permissions/'),
};

export const workflowsAPI = {
  list: () => api.get('/workflows/'),
  create: (data) => api.post('/workflows/', data),
  get: (id) => api.get(`/workflows/${id}/`),
  update: (id, data) => api.put(`/workflows/${id}/`, data),
  delete: (id) => api.delete(`/workflows/${id}/`),
  states: (workflowId) => api.get(`/workflows/${workflowId}/states/`),
  createState: (workflowId, data) => api.post(`/workflows/${workflowId}/states/`, data),
  transitions: (workflowId) => api.get(`/workflows/${workflowId}/transitions/`),
  createTransition: (workflowId, data) => api.post(`/workflows/${workflowId}/transitions/`, data),
  applyToIncident: (incidentId, data) => api.post(`/workflows/incidents/${incidentId}/apply/`, data),
  transitionIncident: (incidentId, data) => api.post(`/workflows/incidents/${incidentId}/transition/`, data),
  incidentStatus: (incidentId) => api.get(`/workflows/incidents/${incidentId}/status/`),
  dashboard: () => api.get('/workflows/dashboard/'),
};

export const auditAPI = {
<<<<<<< HEAD
  logs: (params) => api.get('/audit/logs/list/', { params }),
  get: (id) => api.get(`/audit/logs/${id}/`),
  dashboard: () => api.get('/audit/dashboard/'),
  userActivity: (userId) => api.get(`/audit/users/${userId}/activity/`),
  resourceActivity: (resourceType, resourceId) => api.get(`/audit/resources/${resourceType}/${resourceId}/activity/`),
=======
  logs: (params) => api.get('/audit/logs/', { params }),
  actionChoices: () => api.get('/audit/action-choices/'),
>>>>>>> 674c244 (tus cambios)
};

// Document Traceability APIs
export const visitReportsAPI = {
  list: (params) => api.get('/documents/visit-reports/', { params }),
  create: (data) => api.post('/documents/visit-reports/', data),
  get: (id) => api.get(`/documents/visit-reports/${id}/`),
  update: (id, data) => api.put(`/documents/visit-reports/${id}/`, data),
  delete: (id) => api.delete(`/documents/visit-reports/${id}/`),
  generateOrderNumber: () => api.get('/documents/generate-order-number/'),
};

export const labReportsAPI = {
  list: (params) => api.get('/documents/lab-reports/', { params }),
  create: (data) => api.post('/documents/lab-reports/', data),
  get: (id) => api.get(`/documents/lab-reports/${id}/`),
  update: (id, data) => api.put(`/documents/lab-reports/${id}/`, data),
  delete: (id) => api.delete(`/documents/lab-reports/${id}/`),
};

export const supplierReportsAPI = {
  list: (params) => api.get('/documents/supplier-reports/', { params }),
  create: (data) => api.post('/documents/supplier-reports/', data),
  get: (id) => api.get(`/documents/supplier-reports/${id}/`),
  update: (id, data) => api.put(`/documents/supplier-reports/${id}/`, data),
  delete: (id) => api.delete(`/documents/supplier-reports/${id}/`),
};

// Extended documents API with new methods
documentsAPI.createVisitReport = (data) => api.post('/documents/visit-reports/', data);
documentsAPI.createLabReport = (data) => api.post('/documents/lab-reports/', data);
documentsAPI.createSupplierReport = (data) => api.post('/documents/supplier-reports/', data);

// Dashboard API
export const dashboardAPI = {
  getMetrics: () => api.get('/dashboard/metrics/'),
};

export default api;
