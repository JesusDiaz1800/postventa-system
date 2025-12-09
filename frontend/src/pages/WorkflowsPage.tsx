import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  DocumentDuplicateIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  PlayIcon,
  PauseIcon,
  ArrowPathIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface WorkflowData {
  id: string;
  name: string;
  description: string;
  incident_type: string;
  is_active: boolean;
  states_count: number;
  transitions_count: number;
  created_at: string;
  updated_at: string;
}

export function WorkflowsPage() {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Fetch workflows from API
  const { data: workflows, isLoading, error, refetch } = useQuery({
    queryKey: ['workflows'],
    queryFn: async (): Promise<WorkflowData[]> => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/workflows/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar workflows');
      }
      
      const apiData = await response.json();
      return apiData.results || apiData;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
<<<<<<< HEAD
    cacheTime: 10 * 60 * 1000, // 10 minutes
=======
    gcTime: 10 * 60 * 1000, // 10 minutes
>>>>>>> 674c244 (tus cambios)
  });

  // Mutations
  const toggleStatusMutation = useMutation({
    mutationFn: async (workflowId: string) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/workflows/${workflowId}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
<<<<<<< HEAD
        body: JSON.stringify({ is_active: !workflows?.find(w => w.id === workflowId)?.is_active }),
=======
        body: JSON.stringify({ is_active: !(workflows as any)?.find((w: any) => w.id === workflowId)?.is_active }),
>>>>>>> 674c244 (tus cambios)
      });
      
      if (!response.ok) {
        throw new Error('Error al cambiar estado del workflow');
      }
      
      return response.json();
    },
    onSuccess: () => {
<<<<<<< HEAD
      queryClient.invalidateQueries(['workflows']);
=======
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
>>>>>>> 674c244 (tus cambios)
    },
  });

  const deleteWorkflowMutation = useMutation({
    mutationFn: async (workflowId: string) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/workflows/${workflowId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar workflow');
      }
    },
    onSuccess: () => {
<<<<<<< HEAD
      queryClient.invalidateQueries(['workflows']);
=======
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
>>>>>>> 674c244 (tus cambios)
      setShowDeleteModal(false);
      setSelectedWorkflow(null);
    },
  });

  // Handlers
  const handleToggleStatus = (workflow: WorkflowData) => {
    toggleStatusMutation.mutate(workflow.id);
  };

  const handleEdit = (workflow: WorkflowData) => {
    setSelectedWorkflow(workflow);
    setShowEditModal(true);
  };

  const handleDelete = (workflow: WorkflowData) => {
    setSelectedWorkflow(workflow);
    setShowDeleteModal(true);
  };

  const handleViewDetails = (workflow: WorkflowData) => {
    setSelectedWorkflow(workflow);
    // Aquí podrías abrir un modal de detalles o navegar a una página de detalles
    console.log('Ver detalles del workflow:', workflow);
  };

  const handleRefresh = () => {
    refetch();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <DocumentDuplicateIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar workflows</h3>
        <p className="text-gray-600">Por favor, intenta recargar la página</p>
      </div>
    );
  }

  return (
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Workflows</h1>
              <p className="text-gray-600">Configura flujos de trabajo para diferentes tipos de incidencias</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={handleRefresh}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Actualizar
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Nuevo Workflow
              </button>
            </div>
          </div>
        </div>

        {/* Workflows Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
<<<<<<< HEAD
          {workflows?.map((workflow) => (
=======
          {(workflows as any)?.map((workflow: any) => (
>>>>>>> 674c244 (tus cambios)
            <div key={workflow.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DocumentDuplicateIcon className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">{workflow.name}</h3>
                    <p className="text-sm text-gray-500">{workflow.incident_type}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <button 
                    onClick={() => handleViewDetails(workflow)}
                    className="text-blue-600 hover:text-blue-800 p-1 rounded"
                    title="Ver detalles"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button 
                    onClick={() => handleEdit(workflow)}
                    className="text-indigo-600 hover:text-indigo-800 p-1 rounded"
                    title="Editar workflow"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button 
                    onClick={() => handleToggleStatus(workflow)}
                    className={`p-1 rounded ${workflow.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'}`}
                    title={workflow.is_active ? 'Desactivar workflow' : 'Activar workflow'}
                  >
                    {workflow.is_active ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
                  </button>
                  <button 
                    onClick={() => handleDelete(workflow)}
                    className="text-red-600 hover:text-red-800 p-1 rounded"
                    title="Eliminar workflow"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-4">{workflow.description}</p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>{workflow.states_count} estados</span>
                  <span>{workflow.transitions_count} transiciones</span>
                </div>
                <div className="flex items-center">
                  {workflow.is_active ? (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      <PlayIcon className="h-3 w-3 mr-1" />
                      Activo
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      <PauseIcon className="h-3 w-3 mr-1" />
                      Inactivo
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

<<<<<<< HEAD
        {workflows?.length === 0 && (
=======
        {(workflows as any)?.length === 0 && (
>>>>>>> 674c244 (tus cambios)
          <div className="text-center py-12">
            <DocumentDuplicateIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay workflows</h3>
            <p className="text-gray-600">Crea tu primer workflow para automatizar procesos</p>
          </div>
        )}
      </div>
  );
}

export default WorkflowsPage;