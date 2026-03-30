import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

// Hook para sistemas externos
export const useExternalSystems = (filters = {}) => {
  return useQuery({
    queryKey: ['external-systems', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/integrations/external-systems/?${params}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useExternalSystem = (id) => {
  return useQuery({
    queryKey: ['external-system', id],
    queryFn: async () => {
      const response = await api.get(`/integrations/external-systems/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateExternalSystem = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/integrations/external-systems/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['external-systems']);
    },
  });
};

export const useUpdateExternalSystem = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.put(`/integrations/external-systems/${id}/`, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['external-systems']);
      queryClient.invalidateQueries(['external-system', variables.id]);
    },
  });
};

export const useDeleteExternalSystem = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/integrations/external-systems/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['external-systems']);
    },
  });
};

export const useTestExternalSystemConnection = () => {
  return useMutation({
    mutationFn: async ({ id, testConfig }) => {
      const response = await api.post(`/integrations/external-systems/${id}/test_connection/`, testConfig);
      return response.data;
    },
  });
};

// Hook para plantillas de integración
export const useIntegrationTemplates = (filters = {}) => {
  return useQuery({
    queryKey: ['integration-templates', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/integrations/templates/?${params}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useIntegrationTemplate = (id) => {
  return useQuery({
    queryKey: ['integration-template', id],
    queryFn: async () => {
      const response = await api.get(`/integrations/templates/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateIntegrationTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/integrations/templates/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['integration-templates']);
    },
  });
};

export const useUpdateIntegrationTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.put(`/integrations/templates/${id}/`, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['integration-templates']);
      queryClient.invalidateQueries(['integration-template', variables.id]);
    },
  });
};

export const useDeleteIntegrationTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/integrations/templates/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['integration-templates']);
    },
  });
};

export const useExecuteIntegrationTemplate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, inputData }) => {
      const response = await api.post(`/integrations/templates/${id}/execute/`, inputData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['integration-instances']);
    },
  });
};

export const useTestIntegrationTemplate = () => {
  return useMutation({
    mutationFn: async ({ id, testData }) => {
      const response = await api.post(`/integrations/templates/${id}/test/`, testData);
      return response.data;
    },
  });
};

// Hook para instancias de integración
export const useIntegrationInstances = (filters = {}) => {
  return useQuery({
    queryKey: ['integration-instances', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/integrations/instances/?${params}`);
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
};

export const useIntegrationInstance = (id) => {
  return useQuery({
    queryKey: ['integration-instance', id],
    queryFn: async () => {
      const response = await api.get(`/integrations/instances/${id}/`);
      return response.data;
    },
    enabled: !!id,
    refetchInterval: 5000, // Refrescar cada 5 segundos para instancias activas
  });
};

export const useCancelIntegrationInstance = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/integrations/instances/${id}/cancel/`);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['integration-instances']);
      queryClient.invalidateQueries(['integration-instance', variables]);
    },
  });
};

export const useRetryIntegrationInstance = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/integrations/instances/${id}/retry/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['integration-instances']);
    },
  });
};

// Hook para logs de integración
export const useIntegrationLogs = (filters = {}) => {
  return useQuery({
    queryKey: ['integration-logs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/integrations/logs/?${params}`);
      return response.data;
    },
    staleTime: 30 * 1000, // 30 segundos
  });
};

// Hook para endpoints de webhook
export const useWebhookEndpoints = (filters = {}) => {
  return useQuery({
    queryKey: ['webhook-endpoints', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/integrations/webhook-endpoints/?${params}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useWebhookEndpoint = (id) => {
  return useQuery({
    queryKey: ['webhook-endpoint', id],
    queryFn: async () => {
      const response = await api.get(`/integrations/webhook-endpoints/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateWebhookEndpoint = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/integrations/webhook-endpoints/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['webhook-endpoints']);
    },
  });
};

export const useUpdateWebhookEndpoint = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.put(`/integrations/webhook-endpoints/${id}/`, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['webhook-endpoints']);
      queryClient.invalidateQueries(['webhook-endpoint', variables.id]);
    },
  });
};

export const useDeleteWebhookEndpoint = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/integrations/webhook-endpoints/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['webhook-endpoints']);
    },
  });
};

export const useTestWebhookEndpoint = () => {
  return useMutation({
    mutationFn: async ({ id, testConfig }) => {
      const response = await api.post(`/integrations/webhook-endpoints/${id}/test/`, testConfig);
      return response.data;
    },
  });
};

// Hook para logs de webhook
export const useWebhookLogs = (filters = {}) => {
  return useQuery({
    queryKey: ['webhook-logs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/integrations/webhook-logs/?${params}`);
      return response.data;
    },
    staleTime: 30 * 1000, // 30 segundos
  });
};

// Hook para estadísticas
export const useIntegrationStatistics = () => {
  return useQuery({
    queryKey: ['integration-statistics'],
    queryFn: async () => {
      const [externalSystemsResponse, instancesResponse, webhooksResponse] = await Promise.all([
        api.get('/integrations/external-systems/statistics/'),
        api.get('/integrations/instances/statistics/'),
        api.get('/integrations/webhook-endpoints/statistics/'),
      ]);
      
      return {
        externalSystems: externalSystemsResponse.data,
        instances: instancesResponse.data,
        webhooks: webhooksResponse.data,
      };
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};
