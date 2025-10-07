import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

// Hook para gestión de workflows
export const useWorkflows = () => {
  const queryClient = useQueryClient();

  // Obtener workflows del usuario
  const { data: workflows, isLoading, error } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => api.get('/workflows/instances/my_workflows/').then(res => res.data),
    staleTime: 30000, // 30 segundos
  });

  // Obtener workflows pendientes de aprobación
  const { data: pendingApprovals } = useQuery({
    queryKey: ['workflows', 'pending-approvals'],
    queryFn: () => api.get('/workflows/instances/pending_approvals/').then(res => res.data),
    staleTime: 10000, // 10 segundos
    refetchInterval: 30000, // Refrescar cada 30 segundos
  });

  // Obtener workflows vencidos
  const { data: overdueWorkflows } = useQuery({
    queryKey: ['workflows', 'overdue'],
    queryFn: () => api.get('/workflows/instances/overdue/').then(res => res.data),
    staleTime: 60000, // 1 minuto
  });

  // Crear workflow
  const createWorkflowMutation = useMutation({
    mutationFn: (workflowData) => 
      api.post('/workflows/instances/', workflowData),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflows']);
    },
  });

  // Iniciar workflow
  const startWorkflowMutation = useMutation({
    mutationFn: (workflowId) => 
      api.post(`/workflows/instances/${workflowId}/start/`),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflows']);
    },
  });

  // Cancelar workflow
  const cancelWorkflowMutation = useMutation({
    mutationFn: ({ workflowId, reason }) => 
      api.post(`/workflows/instances/${workflowId}/cancel/`, { reason }),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflows']);
    },
  });

  // Avanzar workflow
  const advanceWorkflowMutation = useMutation({
    mutationFn: ({ workflowId, actionData }) => 
      api.post(`/workflows/instances/${workflowId}/advance/`, actionData),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflows']);
    },
  });

  return {
    workflows,
    pendingApprovals,
    overdueWorkflows,
    isLoading,
    error,
    createWorkflow: createWorkflowMutation.mutate,
    startWorkflow: startWorkflowMutation.mutate,
    cancelWorkflow: cancelWorkflowMutation.mutate,
    advanceWorkflow: advanceWorkflowMutation.mutate,
    isCreating: createWorkflowMutation.isLoading,
    isStarting: startWorkflowMutation.isLoading,
    isCancelling: cancelWorkflowMutation.isLoading,
    isAdvancing: advanceWorkflowMutation.isLoading,
  };
};

// Hook para plantillas de workflow
export const useWorkflowTemplates = () => {
  const { data: templates, isLoading } = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: () => api.get('/workflows/templates/').then(res => res.data),
    staleTime: 300000, // 5 minutos
  });

  // Obtener plantilla por defecto
  const getDefaultTemplate = useCallback((workflowType) => {
    return api.get(`/workflows/templates/default/?type=${workflowType}`).then(res => res.data);
  }, []);

  // Obtener plantillas por tipo
  const getTemplatesByType = useCallback((workflowType) => {
    return api.get(`/workflows/templates/by_type/?type=${workflowType}`).then(res => res.data);
  }, []);

  return {
    templates,
    isLoading,
    getDefaultTemplate,
    getTemplatesByType,
  };
};

// Hook para aprobaciones de workflow
export const useWorkflowApprovals = () => {
  const queryClient = useQueryClient();

  // Obtener aprobaciones pendientes
  const { data: pendingApprovals, isLoading } = useQuery({
    queryKey: ['workflow-approvals', 'pending'],
    queryFn: () => api.get('/workflows/approvals/pending/').then(res => res.data),
    staleTime: 10000, // 10 segundos
    refetchInterval: 30000, // Refrescar cada 30 segundos
  });

  // Obtener aprobaciones vencidas
  const { data: overdueApprovals } = useQuery({
    queryKey: ['workflow-approvals', 'overdue'],
    queryFn: () => api.get('/workflows/approvals/overdue/').then(res => res.data),
    staleTime: 60000, // 1 minuto
  });

  // Aprobar workflow
  const approveWorkflowMutation = useMutation({
    mutationFn: ({ approvalId, comments, metadata }) => 
      api.post(`/workflows/approvals/${approvalId}/approve/`, { comments, metadata }),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflow-approvals']);
      queryClient.invalidateQueries(['workflows']);
    },
  });

  // Rechazar workflow
  const rejectWorkflowMutation = useMutation({
    mutationFn: ({ approvalId, comments, justification, metadata }) => 
      api.post(`/workflows/approvals/${approvalId}/reject/`, { comments, justification, metadata }),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflow-approvals']);
      queryClient.invalidateQueries(['workflows']);
    },
  });

  // Delegar aprobación
  const delegateApprovalMutation = useMutation({
    mutationFn: ({ approvalId, delegatedToId, comments }) => 
      api.post(`/workflows/approvals/${approvalId}/delegate/`, { delegated_to: delegatedToId, comments }),
    onSuccess: () => {
      queryClient.invalidateQueries(['workflow-approvals']);
      queryClient.invalidateQueries(['workflows']);
    },
  });

  return {
    pendingApprovals,
    overdueApprovals,
    isLoading,
    approveWorkflow: approveWorkflowMutation.mutate,
    rejectWorkflow: rejectWorkflowMutation.mutate,
    delegateApproval: delegateApprovalMutation.mutate,
    isApproving: approveWorkflowMutation.isLoading,
    isRejecting: rejectWorkflowMutation.isLoading,
    isDelegating: delegateApprovalMutation.isLoading,
  };
};

// Hook para historial de workflow
export const useWorkflowHistory = () => {
  const { data: history, isLoading } = useQuery({
    queryKey: ['workflow-history'],
    queryFn: () => api.get('/workflows/history/').then(res => res.data),
    staleTime: 60000, // 1 minuto
  });

  return {
    history,
    isLoading,
  };
};

// Hook para estadísticas de workflow
export const useWorkflowStats = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['workflow-stats'],
    queryFn: () => api.get('/workflows/stats/stats/').then(res => res.data),
    staleTime: 300000, // 5 minutos
  });

  return {
    stats,
    isLoading,
  };
};

// Hook para dashboard de workflow
export const useWorkflowDashboard = () => {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['workflow-dashboard'],
    queryFn: () => api.get('/workflows/stats/dashboard/').then(res => res.data),
    staleTime: 60000, // 1 minuto
    refetchInterval: 300000, // Refrescar cada 5 minutos
  });

  return {
    dashboard,
    isLoading,
  };
};

// Hook para búsqueda de workflows
export const useWorkflowSearch = () => {
  const queryClient = useQueryClient();

  const searchWorkflowsMutation = useMutation({
    mutationFn: (searchParams) => 
      api.post('/workflows/search/search/', searchParams),
  });

  return {
    searchWorkflows: searchWorkflowsMutation.mutate,
    searchResults: searchWorkflowsMutation.data,
    isSearching: searchWorkflowsMutation.isLoading,
    searchError: searchWorkflowsMutation.error,
  };
};

// Hook para reglas de workflow
export const useWorkflowRules = () => {
  const { data: rules, isLoading } = useQuery({
    queryKey: ['workflow-rules'],
    queryFn: () => api.get('/workflows/rules/').then(res => res.data),
    staleTime: 300000, // 5 minutos
  });

  return {
    rules,
    isLoading,
  };
};

// Hook para progreso de workflow
export const useWorkflowProgress = (workflowId) => {
  const { data: progress, isLoading } = useQuery({
    queryKey: ['workflow-progress', workflowId],
    queryFn: () => api.get(`/workflows/instances/${workflowId}/progress/`).then(res => res.data),
    staleTime: 30000, // 30 segundos
    enabled: !!workflowId,
  });

  return {
    progress,
    isLoading,
  };
};
