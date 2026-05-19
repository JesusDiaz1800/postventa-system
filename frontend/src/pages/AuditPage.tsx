
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import {
  ClipboardDocumentCheckIcon,
  TrashIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  CalendarDaysIcon,
  UserIcon,
  TagIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import ConfirmationModal from '../components/ConfirmationModal';
import MonitoringTab from '../components/MonitoringTab';
import { CpuChipIcon } from '@heroicons/react/24/outline';

// --- Components ---

const Badge = ({ children, color = 'gray' }) => {
  const colorBit = {
    gray: 'bg-gray-100 text-gray-800 ring-gray-600/20',
    red: 'bg-red-50 text-red-700 ring-red-600/10',
    yellow: 'bg-yellow-50 text-yellow-800 ring-yellow-600/20',
    green: 'bg-green-50 text-green-700 ring-green-600/20',
    blue: 'bg-blue-50 text-blue-700 ring-blue-700/10',
    indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-700/10',
    purple: 'bg-purple-50 text-purple-700 ring-purple-700/10',
    pink: 'bg-pink-50 text-pink-700 ring-pink-700/10',
  }[color] || 'bg-gray-50 text-gray-600 ring-gray-500/10';

  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${colorBit}`}>
      {children}
    </span>
  );
};

const Pagination = ({ page, totalPages, setPage }) => (
  <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
    <div className="flex flex-1 justify-between sm:hidden">
      <button
        onClick={() => setPage(Math.max(1, page - 1))}
        disabled={page === 1}
        className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
      >
        Anterior
      </button>
      <button
        onClick={() => setPage(Math.min(totalPages, page + 1))}
        disabled={page === totalPages}
        className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
      >
        Siguiente
      </button>
    </div>
    <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
      <div>
        <p className="text-sm text-gray-700">
          Página <span className="font-medium">{page}</span> de <span className="font-medium">{totalPages}</span>
        </p>
      </div>
      <div>
        <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
          >
            <span className="sr-only">Anterior</span>
            <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
          </button>
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
          >
            <span className="sr-only">Siguiente</span>
            <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
          </button>
        </nav>
      </div>
    </div>
  </div>
);

const AuditLogTable = ({ logs, page, totalPages, setPage, actionChoices, onViewDetails }) => {
  // Helper to get label from choices
  const getActionLabel = (code) => {
    const choice = actionChoices.find(c => c.value === code);
    return choice ? choice.label : code;
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleString('es-CL');
  };

  return (
    <div className="bg-white shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-300 border-separate border-spacing-0">
          <thead className="bg-slate-50/50 sticky top-0 z-10">
            <tr>
              <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest pl-8 border-b border-slate-200">
                Fecha
              </th>
              <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-200">
                Usuario
              </th>
              <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-200">
                Acción
              </th>
              <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-200">
                Descripción
              </th>
              <th scope="col" className="relative py-4 pl-3 pr-8 text-right text-[11px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-200">
                Detalles
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {logs.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-10 text-center text-gray-500 italic">
                  No se encontraron registros de auditoría con los filtros actuales.
                </td>
              </tr>
            ) : (
              logs.map((log) => {
                const colorRaw = log.action_color || 'text-gray-600';
                const colorMatch = colorRaw.match(/text-([a-z]+)-\d+/);
                const badgeColor = colorMatch ? colorMatch[1] : 'gray';

                return (
                  <tr 
                    key={log.id} 
                    className="hover:bg-indigo-50/30 transition-colors group cursor-pointer"
                    onClick={() => onViewDetails(log)}
                  >
                    <td className="whitespace-nowrap py-4 pl-6 pr-3 text-sm text-gray-500 font-medium">
                      {formatTime(log.timestamp)}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm font-semibold text-gray-900">
                      <div className="flex items-center gap-2">
                        <div className="h-6 w-6 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-xs shadow-sm">
                          {log.user?.username ? log.user.username.charAt(0).toUpperCase() : '?'}
                        </div>
                        {log.user?.username || 'Sistema'}
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                      <div className="flex items-center">
                        <span className="mr-2 text-lg">{log.action_icon}</span>
                        <Badge color={badgeColor}>{getActionLabel(log.action)}</Badge>
                      </div>
                    </td>
                    <td className="px-3 py-4 text-sm text-gray-600 max-w-sm truncate group-hover:text-indigo-700 transition-colors" title={log.description}>
                      {log.description}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-8 text-right text-sm">
                      <button className="text-indigo-600 hover:text-indigo-900 font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                        Ver Más
                      </button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
      <Pagination page={page} totalPages={totalPages} setPage={setPage} />
    </div>
  );
};

const RecycleBinTable = ({ items, onRestore, loading, onDeletePermanent }) => (
  <div className="bg-white shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg overflow-hidden">
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-red-50/50 border-b border-red-100">
          <tr>
            <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-red-400 uppercase tracking-widest pl-8">
              Elemento Eliminado
            </th>
            <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-red-400 uppercase tracking-widest">
              Eliminado Por
            </th>
            <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-red-400 uppercase tracking-widest">
              Fecha Eliminación
            </th>
            <th scope="col" className="px-6 py-4 text-left text-[11px] font-black text-red-400 uppercase tracking-widest">
              Expira en
            </th>
            <th scope="col" className="relative py-4 pl-3 pr-8 sm:pr-8 text-right text-[11px] font-black text-red-400 uppercase tracking-widest">
              Gestión
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {items.length === 0 ? (
            <tr>
              <td colSpan="5" className="px-6 py-10 text-center text-gray-500 italic">
                La papelera de reciclaje está vacía. ¡Excelente!
              </td>
            </tr>
          ) : (
            items.map((item) => (
              <tr key={item.id} className="hover:bg-red-50/30 transition-colors">
                <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-bold text-gray-900 sm:pl-6">
                  <div className="flex flex-col">
                    <span className="text-base text-gray-800">{item.object_repr || item.model_name}</span>
                    <span className="text-xs text-gray-400 font-normal">
                      {item.model_name} #{item.original_id}
                    </span>
                  </div>
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-700">
                  {item.deleted_by_username || 'Sistema'}
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  {new Date(item.deleted_at).toLocaleString('es-CL')}
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${item.days_remaining < 1 ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                    }`}>
                    {item.days_remaining} días
                  </span>
                </td>
                <td className="relative whitespace-nowrap py-4 pl-3 pr-8 text-right text-sm font-medium sm:pr-8">
                  <div className="flex justify-end gap-2 opacity-80 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onDeletePermanent(item.id)}
                      className="h-9 w-9 flex items-center justify-center rounded-xl bg-red-50 text-red-600 hover:bg-red-600 hover:text-white transition-all shadow-sm ring-1 ring-red-100 hover:ring-red-600"
                      title="Eliminar permanentemente"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => onRestore(item)}
                      disabled={loading}
                      className="h-9 w-9 flex items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm ring-1 ring-emerald-100 hover:ring-emerald-600"
                      title="Restaurar"
                    >
                      <ArrowPathIcon className="h-5 w-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  </div>
);

// --- Main Page ---

const AuditPage = () => {
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialTab = queryParams.get('tab') || 'logs';
  
  const [activeTab, setActiveTab] = useState(initialTab); // 'logs', 'bin', or 'health'
  const [restoreItem, setRestoreItem] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);

  // Filters State
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedAction, setSelectedAction] = useState('');

  // Debounce search
  const [debouncedSearch, setDebouncedSearch] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 500);
    return () => clearTimeout(timer);
  }, [search]);

  // Fetch Action Choices
  const { data: actionChoices = [] } = useQuery({
    queryKey: ['audit-action-choices'],
    queryFn: async () => {
      // Endpoint actions under the logs viewset
      const response = await api.get('/audit/logs/action_choices/');
      return response.data.choices || [];
    },
    staleTime: 600000 // Cache for 10 min
  });

  // Fetch Logs
  const { data: logsData, isLoading: logsLoading } = useQuery({
    queryKey: ['audit-logs', page, debouncedSearch, selectedUser, selectedAction],
    queryFn: async () => {
      const params = {
        page,
        page_size: 15,
        search: debouncedSearch,
        user: selectedUser,
        action: selectedAction
      };
      const response = await api.get('/audit/logs/', { params });
      return response.data;
    },
    keepPreviousData: true,
    staleTime: 5000
  });

  const logs = logsData?.results || [];
  const totalPages = logsData?.total_pages || 1;

  // Fetch Recycle Bin
  const { data: deletedItemsData, isLoading: binLoading, refetch: refetchBin } = useQuery({
    queryKey: ['deleted-items'],
    queryFn: async () => {
      const response = await api.get('/audit/deleted-items/');
      return response.data;
    },
    enabled: activeTab === 'bin'
  });

  const deletedItems = Array.isArray(deletedItemsData) ? deletedItemsData : (deletedItemsData?.results || []);

  // Restore Mutation
  const restoreMutation = useMutation({
    mutationFn: async (itemId) => {
      const response = await api.post(`/audit/deleted-items/${itemId}/restore/`);
      return response.data;
    },
    onSuccess: () => {
      showSuccess("Elemento restaurado exitosamente.");
      refetchBin();
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['audit-logs'] });
      setRestoreItem(null);
    },
    onError: (err) => {
      showError(err.response?.data?.error || "Error al restaurar elemento.");
      setRestoreItem(null);
    }
  });

  // Delete Permanently Mutation
  const deleteMutation = useMutation({
    mutationFn: async (itemId) => {
      await api.delete(`/audit/deleted-items/${itemId}/`);
    },
    onSuccess: () => {
      showSuccess("Elemento eliminado permanentemente.");
      refetchBin();
    },
    onError: () => showError("Error al eliminar elemento de la papelera.")
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          {/* Title handled by Global Header (App Layout), but we can add subtitles */}
          <p className="text-sm text-gray-500 mt-1">
            Supervisa la actividad del sistema y gestiona la recuperación de datos.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('logs')}
            className={`${activeTab === 'logs'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              } group inline-flex items-center border-b-2 py-4 px-1 text-sm font-medium transition-colors`}
          >
            <ClipboardDocumentCheckIcon
              className={`-ml-0.5 mr-2 h-5 w-5 ${activeTab === 'logs' ? 'text-indigo-500' : 'text-gray-400 group-hover:text-gray-500'}`}
              aria-hidden="true"
            />
            <span>Logs de Actividad</span>
          </button>
          <button
            onClick={() => setActiveTab('bin')}
            className={`${activeTab === 'bin'
              ? 'border-red-500 text-red-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              } group inline-flex items-center border-b-2 py-4 px-1 text-sm font-medium transition-colors`}
          >
            <TrashIcon
              className={`-ml-0.5 mr-2 h-5 w-5 ${activeTab === 'bin' ? 'text-red-500' : 'text-gray-400 group-hover:text-gray-500'}`}
              aria-hidden="true"
            />
            <span>Papelera de Reciclaje</span>
            <span className="ml-2 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 hidden md:inline-block">
              Admin
            </span>
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`${activeTab === 'health'
              ? 'border-emerald-500 text-emerald-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              } group inline-flex items-center border-b-2 py-4 px-1 text-sm font-medium transition-colors`}
          >
            <CpuChipIcon
              className={`-ml-0.5 mr-2 h-5 w-5 ${activeTab === 'health' ? 'text-emerald-500' : 'text-gray-400 group-hover:text-gray-500'}`}
              aria-hidden="true"
            />
            <span>Salud del Sistema</span>
          </button>
        </nav>
      </div>

      {/* Main Content Area */}
      {activeTab === 'logs' ? (
        <div className="space-y-4">
          {/* Filters Bar */}
          <div className="grid grid-cols-1 gap-y-4 sm:grid-cols-2 md:grid-cols-4 md:gap-x-4 bg-white p-4 shadow-sm rounded-lg border border-gray-100">
            {/* Search */}
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" aria-hidden="true" />
              </div>
              <input
                type="text"
                className="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                placeholder="Buscar en logs..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {/* User Filter */}
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <UserIcon className="h-4 w-4 text-gray-400" aria-hidden="true" />
              </div>
              <input
                type="text"
                className="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                placeholder="Filtrar por usuario..."
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
              />
            </div>

            {/* Action Filter */}
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <TagIcon className="h-4 w-4 text-gray-400" aria-hidden="true" />
              </div>
              <select
                className="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                value={selectedAction}
                onChange={(e) => setSelectedAction(e.target.value)}
              >
                <option value="">Todas las acciones</option>
                {actionChoices.map((choice) => (
                  <option key={choice.value} value={choice.value}>
                    {choice.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Reset Filters */}
            <button
              onClick={() => { setSearch(''); setSelectedUser(''); setSelectedAction(''); setPage(1); }}
              className="inline-flex items-center justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              <FunnelIcon className="-ml-0.5 mr-2 h-4 w-4 text-gray-400" aria-hidden="true" />
              Limpiar Filtros
            </button>

            {/* Purge Button (Admin Only) */}
            <button
              onClick={async () => {
                if (window.confirm('¿Seguro que deseas eliminar todos los logs antiguos/inválidos? Esta acción no se puede deshacer.')) {
                  try {
                    const res = await api.post('/audit/logs/purge_logs/');
                    showSuccess(res.data.message);
                    // Invalidamos logs
                    queryClient.invalidateQueries({ queryKey: ['audit-logs'] }).catch(e => console.error("Error invalidating logs:", e));
                  } catch (err) {
                    console.error("Error purging logs:", err);
                    showError("Error al limpiar logs");
                  }
                }
              }}
              className="inline-flex items-center justify-center rounded-md bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 shadow-sm ring-1 ring-inset ring-red-300 hover:bg-red-100"
            >
              <TrashIcon className="-ml-0.5 mr-2 h-4 w-4 text-red-500" aria-hidden="true" />
              Limpiar Logs
            </button>
          </div>

          {/* Table */}
          {logsLoading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-12 bg-gray-200 rounded-lg w-full"></div>
              <div className="h-64 bg-gray-100 rounded-lg w-full"></div>
            </div>
          ) : (
            <AuditLogTable 
              logs={logs} 
              page={page} 
              totalPages={totalPages} 
              setPage={setPage} 
              actionChoices={actionChoices} 
              onViewDetails={setSelectedLog}
            />
          )}
        </div>
      ) : activeTab === 'bin' ? (
        // Recycle Bin Tab
        <div className="space-y-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <ClockIcon className="h-5 w-5 text-yellow-400" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Los elementos en la papelera se eliminan permanentemente después de <span className="font-bold">3 días</span>.
                  Restáuralos si fueron eliminados por error.
                </p>
              </div>
            </div>
          </div>

          {binLoading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-64 bg-gray-100 rounded-lg w-full"></div>
            </div>
          ) : (
            <RecycleBinTable
              items={deletedItems}
              onRestore={setRestoreItem}
              onDeletePermanent={(id) => {
                if (window.confirm("¿Estás seguro de eliminar esto permanentemente? No se podrá recuperar.")) {
                  deleteMutation.mutate(id);
                }
              }}
              loading={restoreMutation.isLoading}
            />
          )}
        </div>
      ) : (
        // Health Tab
        <MonitoringTab />
      )}

      {/* Restore Confirmation */}
      <ConfirmationModal
        isOpen={!!restoreItem}
        onClose={() => setRestoreItem(null)}
        onConfirm={() => restoreItem && restoreMutation.mutate(restoreItem.id)}
        confirmText="Confirmar Restauración"
        title="Restaurar Elemento Eliminado"
        message={restoreItem ? `Vas a restaurar el elemento ${restoreItem.model_name} (ID: ${restoreItem.original_id}). ¿Estás seguro?` : ''}
        type="info"
        isLoading={restoreMutation.isLoading}
      />

      {/* Log Details Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col border border-slate-200 animate-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{selectedLog.action_icon}</span>
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">Detalles de Actividad</h3>
                  <p className="text-xs text-slate-500 font-medium">{new Date(selectedLog.timestamp).toLocaleString('es-CL')}</p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedLog(null)}
                className="p-2 hover:bg-slate-200 rounded-full transition-colors"
              >
                <XMarkIcon className="h-5 w-5 text-slate-500" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Description Card */}
              <div className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4">
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1.5">Descripción</h4>
                <p className="text-slate-700 font-semibold leading-relaxed">{selectedLog.description}</p>
              </div>

              {/* Technical Details (JSON) */}
              <div>
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center">
                  <div className="h-px bg-slate-200 flex-1 mr-3"></div>
                  Información Técnica / Logs
                  <div className="h-px bg-slate-200 flex-1 ml-3"></div>
                </h4>
                <div className="bg-slate-900 rounded-xl p-4 overflow-x-auto shadow-inner ring-1 ring-white/10">
                  <pre className="text-xs text-emerald-400/90 font-mono leading-relaxed">
                    {JSON.stringify(selectedLog.details, null, 2)}
                  </pre>
                </div>
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block mb-0.5">Usuario</span>
                  <span className="text-sm font-semibold text-slate-700">{selectedLog.user?.username || 'Sistema'}</span>
                </div>
                <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block mb-0.5">IP Address</span>
                  <span className="text-sm font-semibold text-slate-700">{selectedLog.ip_address || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-6 py-2 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-200"
              >
                Cerrar Diagnóstico
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* --- Visual Details Helper --- */
const XMarkIcon = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
);

export default AuditPage;