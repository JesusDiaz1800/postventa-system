import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
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
    if (!token) {
      token = localStorage.getItem('access_token');
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('=== TOKEN ADDED TO REQUEST ===');
      console.log('URL:', config.url);
      console.log('Token preview:', token.substring(0, 20) + '...');
    } else {
      console.log('=== NO TOKEN FOUND ===');
      console.log('URL:', config.url);
      console.log('localStorage postventa_auth:', localStorage.getItem('postventa_auth'));
      console.log('localStorage access_token:', localStorage.getItem('access_token'));
    }
    
    // Log request details
    if (config.url?.includes('/users/') && config.method === 'post') {
      console.log('=== AXIOS REQUEST INTERCEPTOR ===');
      console.log('Request URL:', config.url);
      console.log('Request method:', config.method);
      console.log('Request headers:', config.headers);
      console.log('Request data:', config.data);
      console.log('Request data type:', typeof config.data);
      if (config.data) {
        console.log('Request data keys:', Object.keys(config.data));
        console.log('Request data values:', Object.values(config.data));
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
    // Log response details for user operations
    if (response.config?.url?.includes('/users/') && response.config?.method === 'get') {
      console.log('=== AXIOS RESPONSE INTERCEPTOR (GET USERS SUCCESS) ===');
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      console.log('Response data:', response.data);
      console.log('Response data type:', typeof response.data);
      console.log('Response data keys:', Object.keys(response.data));
      if (response.data.results) {
        console.log('Response data.results length:', response.data.results.length);
        console.log('Response data.results type:', typeof response.data.results);
      }
    }
    if (response.config?.url?.includes('/users/') && response.config?.method === 'post') {
      console.log('=== AXIOS RESPONSE INTERCEPTOR (POST USER SUCCESS) ===');
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      console.log('Response data:', response.data);
    }
    return response;
  },
  async (error) => {
    // Log error details for user creation
    if (error.config?.url?.includes('/users/') && error.config?.method === 'post') {
      console.log('=== AXIOS RESPONSE INTERCEPTOR (ERROR) ===');
      console.log('Error status:', error.response?.status);
      console.log('Error headers:', error.response?.headers);
      console.log('Error data:', error.response?.data);
      console.log('Error config:', error.config);
      console.log('Error message:', error.message);
    }
    
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

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
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('postventa_auth');
        delete api.defaults.headers.common['Authorization'];
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  me: () => api.get('/auth/me/'),
  changePassword: (data) => api.put('/auth/change-password/', data),
  refreshToken: (refreshToken) => api.post('/auth/token/refresh/', { refresh: refreshToken }),
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
  create: (data) => {
    console.log('=== API CREATE USER ===');
    console.log('API create data:', data);
    console.log('API create data type:', typeof data);
    console.log('API create data keys:', Object.keys(data));
    console.log('API create data values:', Object.values(data));
    
    // Log each field individually
    Object.entries(data).forEach(([key, value]) => {
      console.log(`API ${key}:`, value, `(type: ${typeof value})`);
    });
    
    return api.post('/users/', data);
  },
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
  logs: (params) => api.get('/audit/logs/list/', { params }),
  get: (id) => api.get(`/audit/logs/${id}/`),
  dashboard: () => api.get('/audit/dashboard/'),
  userActivity: (userId) => api.get(`/audit/users/${userId}/activity/`),
  resourceActivity: (resourceType, resourceId) => api.get(`/audit/resources/${resourceType}/${resourceId}/activity/`),
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
