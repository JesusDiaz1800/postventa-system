import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../utils/api';

// Hook para reglas de monitoreo
export const useMonitoringRules = (filters = {}) => {
  return useQuery({
    queryKey: ['monitoring-rules', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/rules/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useMonitoringRule = (id) => {
  return useQuery({
    queryKey: ['monitoring-rule', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/rules/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateMonitoringRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/rules/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
    },
  });
};

export const useUpdateMonitoringRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/rules/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-rule', id] });
    },
  });
};

export const useDeleteMonitoringRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/rules/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
    },
  });
};

export const useTestMonitoringRule = () => {
  return useMutation({
    mutationFn: async ({ id, options = {} }) => {
      const response = await api.post(`/monitoring/rules/${id}/test/`, options);
      return response.data;
    },
  });
};

export const useExecuteMonitoringRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/monitoring/rules/${id}/execute/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

export const useExecuteAllMonitoringRules = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.post('/monitoring/rules/execute_all/');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

// Hook para alertas
export const useAlerts = (filters = {}) => {
  return useQuery({
    queryKey: ['alerts', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/alerts/?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

export const useAlert = (id) => {
  return useQuery({
    queryKey: ['alert', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/alerts/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/alerts/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

export const useUpdateAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/alerts/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert', id] });
    },
  });
};

export const useDeleteAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/alerts/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/monitoring/alerts/${id}/acknowledge/`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert', id] });
    },
  });
};

export const useResolveAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/monitoring/alerts/${id}/resolve/`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert', id] });
    },
  });
};

export const useAlertStatistics = (filters = {}) => {
  return useQuery({
    queryKey: ['alert-statistics', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/alerts/statistics/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Hook para valores de métricas
export const useMetricValues = (filters = {}) => {
  return useQuery({
    queryKey: ['metric-values', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/metrics/?${params.toString()}`);
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
};

export const useMetricValue = (id) => {
  return useQuery({
    queryKey: ['metric-value', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/metrics/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateMetricValue = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/metrics/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['metric-values'] });
    },
  });
};

export const useMetricValueStatistics = (filters = {}) => {
  return useQuery({
    queryKey: ['metric-value-statistics', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/metrics/statistics/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Hook para verificaciones de salud
export const useHealthChecks = (filters = {}) => {
  return useQuery({
    queryKey: ['health-checks', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/health-checks/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useHealthCheck = (id) => {
  return useQuery({
    queryKey: ['health-check', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/health-checks/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateHealthCheck = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/health-checks/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health-checks'] });
    },
  });
};

export const useUpdateHealthCheck = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/health-checks/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['health-checks'] });
      queryClient.invalidateQueries({ queryKey: ['health-check', id] });
    },
  });
};

export const useDeleteHealthCheck = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/health-checks/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health-checks'] });
    },
  });
};

export const useExecuteHealthCheck = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/monitoring/health-checks/${id}/execute/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health-checks'] });
      queryClient.invalidateQueries({ queryKey: ['health-check-results'] });
    },
  });
};

export const useExecuteAllHealthChecks = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.post('/monitoring/health-checks/execute_all/');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health-checks'] });
      queryClient.invalidateQueries({ queryKey: ['health-check-results'] });
    },
  });
};

export const useHealthCheckStatistics = () => {
  return useQuery({
    queryKey: ['health-check-statistics'],
    queryFn: async () => {
      const response = await api.get('/monitoring/health-checks/statistics/');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

// Hook para resultados de verificaciones de salud
export const useHealthCheckResults = (filters = {}) => {
  return useQuery({
    queryKey: ['health-check-results', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/health-check-results/?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

// Hook para métricas del sistema
export const useSystemMetrics = (filters = {}) => {
  return useQuery({
    queryKey: ['system-metrics', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/system-metrics/?${params.toString()}`);
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
};

export const useSystemMetric = (id) => {
  return useQuery({
    queryKey: ['system-metric', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/system-metrics/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateSystemMetric = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/system-metrics/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-metrics'] });
    },
  });
};

export const useSystemMetricStatistics = (filters = {}) => {
  return useQuery({
    queryKey: ['system-metric-statistics', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/system-metrics/statistics/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Hook para canales de notificación
export const useNotificationChannels = (filters = {}) => {
  return useQuery({
    queryKey: ['notification-channels', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/notification-channels/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useNotificationChannel = (id) => {
  return useQuery({
    queryKey: ['notification-channel', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/notification-channels/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateNotificationChannel = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/notification-channels/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-channels'] });
    },
  });
};

export const useUpdateNotificationChannel = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/notification-channels/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['notification-channels'] });
      queryClient.invalidateQueries({ queryKey: ['notification-channel', id] });
    },
  });
};

export const useDeleteNotificationChannel = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/notification-channels/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-channels'] });
    },
  });
};

export const useTestNotificationChannel = () => {
  return useMutation({
    mutationFn: async ({ id, options = {} }) => {
      const response = await api.post(`/monitoring/notification-channels/${id}/test/`, options);
      return response.data;
    },
  });
};

// Hook para plantillas de alertas
export const useAlertTemplates = (filters = {}) => {
  return useQuery({
    queryKey: ['alert-templates', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/alert-templates/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useAlertTemplate = (id) => {
  return useQuery({
    queryKey: ['alert-template', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/alert-templates/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateAlertTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/alert-templates/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-templates'] });
    },
  });
};

export const useUpdateAlertTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/alert-templates/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['alert-templates'] });
      queryClient.invalidateQueries({ queryKey: ['alert-template', id] });
    },
  });
};

export const useDeleteAlertTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/alert-templates/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-templates'] });
    },
  });
};

// Hook para dashboards de monitoreo
export const useMonitoringDashboards = (filters = {}) => {
  return useQuery({
    queryKey: ['monitoring-dashboards', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/dashboards/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useMonitoringDashboard = (id) => {
  return useQuery({
    queryKey: ['monitoring-dashboard', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/dashboards/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateMonitoringDashboard = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/dashboards/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboards'] });
    },
  });
};

export const useUpdateMonitoringDashboard = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/dashboards/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboards'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboard', id] });
    },
  });
};

export const useDeleteMonitoringDashboard = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/dashboards/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboards'] });
    },
  });
};

// Hook para widgets de monitoreo
export const useMonitoringWidgets = (filters = {}) => {
  return useQuery({
    queryKey: ['monitoring-widgets', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/monitoring/widgets/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useMonitoringWidget = (id) => {
  return useQuery({
    queryKey: ['monitoring-widget', id],
    queryFn: async () => {
      const response = await api.get(`/monitoring/widgets/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateMonitoringWidget = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/monitoring/widgets/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-widgets'] });
    },
  });
};

export const useUpdateMonitoringWidget = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/monitoring/widgets/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-widgets'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-widget', id] });
    },
  });
};

export const useDeleteMonitoringWidget = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/monitoring/widgets/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-widgets'] });
    },
  });
};

// Hook para estadísticas generales de monitoreo
export const useMonitoringStatistics = () => {
  return useQuery({
    queryKey: ['monitoring-statistics'],
    queryFn: async () => {
      const response = await api.get('/monitoring/statistics/overview/');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};
