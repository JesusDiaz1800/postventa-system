import axios, { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';

// --- Types & Interfaces ---
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  [key: string]: any;
}

// Normalize API base: prefer relative '/api' in dev to utilize Vite Proxy (handling HTTPS->HTTP)
function resolveApiBase(): string {
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
  timeout: 120000, // 120 seconds timeout for long-running AI tasks
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
      // 1. Try localStorage first (Persistent source of truth for Sertec)
      const localAuthRaw = localStorage.getItem('postventa_auth');
      if (localAuthRaw) {
        try {
          const parsed = JSON.parse(localAuthRaw);
          token = parsed.token || parsed.access_token || parsed.access;
        } catch (error) {
          // If JSON is malformed, don't remove yet, try individual keys
        }
      }
      
      if (!token) {
        token = localStorage.getItem('access_token');
      }

      // 2. Fallback to sessionStorage if needed
      if (!token) {
        const sessionAuth = sessionStorage.getItem('postventa_auth');
        if (sessionAuth) {
          try {
            const parsed = JSON.parse(sessionAuth);
            token = parsed.token || parsed.access_token || parsed.access;
          } catch (error) {}
        }
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
      const authRoutes = ['/visits/', '/users/', '/documents/', '/reports/', '/notifications/'];
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

// Incidents API Removed due to deep audit

export const documentsAPI = {
  list: (params?: PaginationParams) => api.get('/documents/', { params }),
  create: (data: any) => api.post('/documents/', data),
  get: (id: string | number) => api.get(`/documents/${id}/`),
  update: (id: string | number, data: any) => api.put(`/documents/${id}/`, data),
  delete: (id: string | number) => api.delete(`/documents/${id}/`),
  generate: (data: any) => api.post('/documents/generate/', data),
  edit: (documentId: string | number, data: any) => api.post(`/documents/${documentId}/edit/`, data),
  convert: (documentId: string | number, data: any) => api.post(`/documents/${documentId}/convert/`, data),
  versions: (documentId: string | number) => api.get(`/documents/${documentId}/versions/`),
  conversions: (documentId: string | number) => api.get(`/documents/${documentId}/conversions/`),
  search: (params: any) => api.get('/documents/search/', { params }),
  
  // Attachments
  listAttachments: (reportId: string | number, type: 'visit' | 'lab' | 'supplier') => 
    api.get(`/documents/report-attachments/${reportId}/${type}/`),
  
  uploadAttachment: (reportId: string | number, type: 'visit' | 'lab' | 'supplier', formData: FormData) => 
    api.post(`/documents/report-attachments/${reportId}/${type}/upload/`, formData),
    
  deleteAttachment: (reportId: string | number, type: 'visit' | 'lab' | 'supplier', attachmentId: number) => 
    api.delete(`/documents/report-attachments/${reportId}/${type}/${attachmentId}/delete/`),
    
  getAttachmentViewUrl: (reportId: string | number, type: 'visit' | 'lab' | 'supplier', attachmentId: number) => 
    `${API_BASE_URL}/documents/report-attachments/${reportId}/${type}/${attachmentId}/view/`,
    
  getAttachmentDownloadUrl: (reportId: string | number, type: 'visit' | 'lab' | 'supplier', attachmentId: number) => 
    `${API_BASE_URL}/documents/report-attachments/${reportId}/${type}/${attachmentId}/download/`,
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

// Core Visit Reports API
export const visitReportsAPI = {
  list: (params) => api.get('/visits/', { params }),
  create: (data) => api.post('/visits/', data),
  get: (id) => api.get(`/visits/${id}/`),
  update: (id, data) => api.patch(`/visits/${id}/`, data),
  delete: (id) => api.delete(`/visits/${id}/`),
  generateOrderNumber: () => api.get('/visits/generate-order-number/'),
  generatePDF: (id, data) => api.post(`/visits/${id}/pdf/`, data, { responseType: 'blob' }),
  sendEmail: (id, recipients) => api.post(`/visits/${id}/send-email/`, { recipients }),
  getIncident: (id) => api.get(`/incidents/${id}/`),
};

export const sapAPI = {
  searchCustomers: (q) => api.get('/sap/customers/search/', { params: { q } }),
  getCustomerProjects: (cardCode) => api.get(`/sap/customers/${cardCode}/projects/`),
  getCustomerDetails: (cardCode) => api.get(`/sap/customer-details/${cardCode}/`),
  getSalesEmployees: () => api.get('/sap/sales-employees/'),
  getTechnicians: (role?: string) => api.get('/sap/technicians/', { params: { role } }),
};

// Dashboard API
export const dashboardAPI = {
  getMetrics: () => api.get('/dashboard/metrics/'),
};

// Notifications API Removido - Sertec Deep Audit

export default api;

