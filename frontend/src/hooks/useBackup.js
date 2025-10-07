import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../utils/api';

// Hook para trabajos de backup
export const useBackupJobs = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-jobs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/jobs/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useBackupJob = (id) => {
  return useQuery({
    queryKey: ['backup-job', id],
    queryFn: async () => {
      const response = await api.get(`/backup/jobs/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateBackupJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/backup/jobs/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-jobs'] });
    },
  });
};

export const useUpdateBackupJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/backup/jobs/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['backup-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['backup-job', id] });
    },
  });
};

export const useDeleteBackupJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/backup/jobs/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-jobs'] });
    },
  });
};

export const useExecuteBackupJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, options = {} }) => {
      const response = await api.post(`/backup/jobs/${id}/execute/`, options);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['backup-instances'] });
    },
  });
};

export const useTestBackupJob = () => {
  return useMutation({
    mutationFn: async ({ id, options = {} }) => {
      const response = await api.post(`/backup/jobs/${id}/test/`, options);
      return response.data;
    },
  });
};

export const useCancelBackupJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/backup/jobs/${id}/cancel/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['backup-instances'] });
    },
  });
};

export const useBackupJobStatistics = () => {
  return useQuery({
    queryKey: ['backup-job-statistics'],
    queryFn: async () => {
      const response = await api.get('/backup/jobs/statistics/');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

// Hook para instancias de backup
export const useBackupInstances = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-instances', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/instances/?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

export const useBackupInstance = (id) => {
  return useQuery({
    queryKey: ['backup-instance', id],
    queryFn: async () => {
      const response = await api.get(`/backup/instances/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useDownloadBackup = () => {
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.get(`/backup/instances/${id}/download/`, {
        responseType: 'blob',
      });
      return response.data;
    },
  });
};

export const useVerifyBackup = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/backup/instances/${id}/verify/`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['backup-instance', id] });
    },
  });
};

export const useBackupInstanceStatistics = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-instance-statistics', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/instances/statistics/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

// Hook para trabajos de restauración
export const useRestoreJobs = (filters = {}) => {
  return useQuery({
    queryKey: ['restore-jobs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/restores/?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

export const useRestoreJob = (id) => {
  return useQuery({
    queryKey: ['restore-job', id],
    queryFn: async () => {
      const response = await api.get(`/backup/restores/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateRestoreJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/backup/restores/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['restore-jobs'] });
    },
  });
};

export const useExecuteRestoreJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, options = {} }) => {
      const response = await api.post(`/backup/restores/${id}/execute/`, options);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['restore-jobs'] });
    },
  });
};

export const useCancelRestoreJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/backup/restores/${id}/cancel/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['restore-jobs'] });
    },
  });
};

// Hook para programaciones de backup
export const useBackupSchedules = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-schedules', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/schedules/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

export const useBackupSchedule = (id) => {
  return useQuery({
    queryKey: ['backup-schedule', id],
    queryFn: async () => {
      const response = await api.get(`/backup/schedules/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateBackupSchedule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/backup/schedules/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-schedules'] });
    },
  });
};

export const useUpdateBackupSchedule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/backup/schedules/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['backup-schedules'] });
      queryClient.invalidateQueries({ queryKey: ['backup-schedule', id] });
    },
  });
};

export const useDeleteBackupSchedule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/backup/schedules/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-schedules'] });
    },
  });
};

export const useExecuteScheduleNow = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/backup/schedules/${id}/execute_now/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-schedules'] });
      queryClient.invalidateQueries({ queryKey: ['backup-instances'] });
    },
  });
};

export const usePauseSchedule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/backup/schedules/${id}/pause/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-schedules'] });
    },
  });
};

export const useResumeSchedule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/backup/schedules/${id}/resume/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-schedules'] });
    },
  });
};

// Hook para almacenamientos de backup
export const useBackupStorages = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-storages', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/storages/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useBackupStorage = (id) => {
  return useQuery({
    queryKey: ['backup-storage', id],
    queryFn: async () => {
      const response = await api.get(`/backup/storages/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateBackupStorage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/backup/storages/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-storages'] });
    },
  });
};

export const useUpdateBackupStorage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/backup/storages/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['backup-storages'] });
      queryClient.invalidateQueries({ queryKey: ['backup-storage', id] });
    },
  });
};

export const useDeleteBackupStorage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/backup/storages/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-storages'] });
    },
  });
};

export const useTestBackupStorage = () => {
  return useMutation({
    mutationFn: async ({ id, options = {} }) => {
      const response = await api.post(`/backup/storages/${id}/test/`, options);
      return response.data;
    },
  });
};

export const useBackupStorageStatistics = () => {
  return useQuery({
    queryKey: ['backup-storage-statistics'],
    queryFn: async () => {
      const response = await api.get('/backup/storages/statistics/');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

// Hook para logs de backup
export const useBackupLogs = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-logs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/logs/?${params.toString()}`);
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
};

// Hook para políticas de backup
export const useBackupPolicies = (filters = {}) => {
  return useQuery({
    queryKey: ['backup-policies', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/backup/policies/?${params.toString()}`);
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
};

export const useBackupPolicy = (id) => {
  return useQuery({
    queryKey: ['backup-policy', id],
    queryFn: async () => {
      const response = await api.get(`/backup/policies/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateBackupPolicy = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/backup/policies/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-policies'] });
    },
  });
};

export const useUpdateBackupPolicy = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/backup/policies/${id}/`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['backup-policies'] });
      queryClient.invalidateQueries({ queryKey: ['backup-policy', id] });
    },
  });
};

export const useDeleteBackupPolicy = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/backup/policies/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backup-policies'] });
    },
  });
};
