import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PaperClipIcon,
  TrashIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  PhotoIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';

const AuthenticatedImage = ({ src, alt, className, onError }) => {
  const [blobUrl, setBlobUrl] = React.useState(null);
  const [error, setError] = React.useState(false);

  React.useEffect(() => {
    if (!src) return;

    // If it's already a data URL or blob, use it directly
    if (src.startsWith('data:') || src.startsWith('blob:')) {
      setBlobUrl(src);
      return;
    }

    // If it's not an API URL, use it directly
    if (!src.includes('/api/')) {
      setBlobUrl(src);
      return;
    }

    let isCancelled = false;
    const fetchImage = async () => {
      try {
        // Strip /api prefix as api instance adds baseURL
        const cleanSrc = src.replace(/^\/api/, '');
        const response = await api.get(cleanSrc, { responseType: 'blob' });
        if (isCancelled) return;
        const url = URL.createObjectURL(response.data);
        setBlobUrl(url);
      } catch (err) {
        console.error('Error fetching image:', err);
        if (!isCancelled) setError(true);
      }
    };

    fetchImage();

    return () => {
      isCancelled = true;
      if (blobUrl && (src.includes('/api/'))) {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [src]);

  if (error) {
    if (onError) onError();
    return null;
  }

  if (!blobUrl) {
    return <div className="w-full h-full bg-slate-100 animate-pulse flex items-center justify-center">
      <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
    </div>;
  }

  return <img src={blobUrl} alt={alt} className={className} />;
};

const IncidentAttachments = ({ incidentId }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  const {
    data: attachmentsData,
    isLoading,
    refetch
  } = useQuery({
    queryKey: ['incident-attachments', incidentId],
    queryFn: async () => {
      if (!incidentId) return { attachments: [] };
      const response = await api.get(`/documents/attachments/incident/${incidentId}/`);
      return response.data;
    },
    enabled: !!incidentId,
  });

  const attachments = attachmentsData?.attachments || [];

  const uploadMutation = useMutation({
    mutationFn: async ({ file, description, isPublic }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('incident_id', incidentId);
      formData.append('document_type', 'incident_attachment');
      formData.append('description', description || file.name);
      formData.append('is_public', isPublic);

      const response = await api.post(
        `/documents/attachments/incident/${incidentId}/upload/`, // Correct endpoint from urls.py
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
      showSuccess('Documento adjuntado correctamente');
      setShowUploadModal(false);
      setSelectedFile(null);
      setDescription('');
      setIsPublic(true);
      setIsUploading(false);
    },
    onError: (error) => {
      console.error(error);
      showError('Error al subir el documento');
      setIsUploading(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (attachment) => {
      if (attachment.model === 'IncidentImage') {
        const realId = attachment.real_id || attachment.id.split('-')[1];
        await api.delete(`/incidents/${incidentId}/images/${realId}/delete/`);
      } else {
        // Default to DocumentAttachment logic
        const realId = attachment.real_id || attachment.id;
        await api.delete(`/documents/attachments/incident/${incidentId}/${realId}/delete/`);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
      showSuccess('Archivo eliminado');
    },
    onError: () => showError('Error al eliminar el archivo'),
  });

  const handleOpen = async (doc) => {
    if (!doc.view_url) {
      showError('No se puede visualizar este archivo');
      return;
    }

    try {
      // If it's not an API URL, just open it
      if (!doc.view_url.includes('/api/')) {
        window.open(doc.view_url, '_blank');
        return;
      }

      // Fetch as blob to include Auth header
      // Strip /api prefix
      const cleanUrl = doc.view_url.replace(/^\/api/, '');
      const response = await api.get(cleanUrl, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: response.headers['content-type'] }));
      window.open(url, '_blank');
      // Note: We don't revokeObjectURL here as it's used in the new tab. 
      // It will be cleaned up when the current page is closed.
    } catch (err) {
      console.error('Error opening document:', err);
      showError('Error al abrir el documento');
    }
  };

  const handleDownload = useCallback(async (attachment) => {
    try {
      if (!attachment.download_url) {
        showError('No hay URL de descarga disponible');
        return;
      }

      // Strip /api prefix
      const cleanUrl = attachment.download_url.replace(/^\/api/, '');
      const response = await api.get(
        cleanUrl,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = attachment.filename || attachment.file_name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      showError('Error en la descarga');
    }
  }, [showError]);

  const handleDelete = useCallback((attachment) => {
    if (window.confirm(`¿Eliminar el archivo "${attachment.file_name || attachment.filename}"?`)) {
      deleteMutation.mutate(attachment);
    }
  }, [deleteMutation]);

  const handleUpload = useCallback(() => {
    if (!selectedFile) return;
    setIsUploading(true);
    uploadMutation.mutate({ file: selectedFile, description, isPublic });
  }, [selectedFile, description, isPublic, uploadMutation]);

  if (!incidentId) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <PaperClipIcon className="w-4 h-4 text-slate-400" />
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">{attachments.length} Archivos / Evidencias</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="text-[10px] font-black uppercase tracking-widest text-indigo-600 hover:text-indigo-800 flex items-center gap-2 bg-indigo-50 px-3 py-1.5 rounded-lg transition-colors"
        >
          <CloudArrowUpIcon className="w-4 h-4" />
          Adjuntar Archivo
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center p-8">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : attachments.length === 0 ? (
        <div className="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
          <DocumentTextIcon className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-xs text-slate-400 font-bold">No hay documentos adjuntos</p>
        </div>
      ) : (
        <div className="space-y-3">
          {attachments.map((doc) => (
            <div key={doc.id} className="flex items-center justify-between p-3 bg-white border border-slate-100 rounded-xl hover:shadow-md transition-shadow group">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-slate-50 rounded-lg flex items-center justify-center text-slate-400 overflow-hidden border border-slate-100">
                  {doc.is_image ? (
                    <AuthenticatedImage
                      src={doc.thumbnail_url || doc.view_url || doc.file_url}
                      alt="Thumbnail"
                      className="w-full h-full object-cover"
                      onError={() => { /* fallback stays handled by AuthenticatedImage internally if it returns null */ }}
                    />
                  ) : (
                    <DocumentTextIcon className="w-6 h-6 text-indigo-400" />
                  )}
                  {doc.is_image && !doc.thumbnail_url && !doc.view_url && <PhotoIcon className="w-6 h-6 text-emerald-400" />}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-slate-700 leading-tight">{doc.description || doc.filename}</p>
                    {doc.is_image && (
                      <span className="text-[8px] font-black bg-emerald-100 text-emerald-600 px-1 rounded uppercase tracking-tighter">Imagen</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="text-[9px] text-slate-400 font-medium flex items-center gap-1">
                      <CalendarIcon className="w-2.5 h-2.5" />
                      {new Date(doc.uploaded_at || doc.created_at).toLocaleDateString()}
                    </span>
                    <span className="text-[9px] text-slate-400 font-medium flex items-center gap-1">
                      <UserIcon className="w-2.5 h-2.5" />
                      {doc.uploaded_by || 'Sistema'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleOpen(doc)}
                  className="p-2 text-slate-400 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 rounded-lg transition-colors"
                  title="Visualizar"
                >
                  <EyeIcon className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDownload(doc)}
                  className="p-2 text-slate-400 hover:text-emerald-600 bg-slate-50 hover:bg-emerald-50 rounded-lg transition-colors"
                  title="Descargar"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                </button>
                {(doc.model === 'DocumentAttachment' || doc.model === 'IncidentImage') && (
                  <button
                    onClick={() => handleDelete(doc)}
                    className="p-2 text-slate-400 hover:text-rose-600 bg-slate-50 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Eliminar"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-[50] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h3 className="text-sm font-black text-slate-800 uppercase tracking-widest">Adjuntar Documento</h3>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-rose-500 transition-colors">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="space-y-4">
                <label className="block text-center border-2 border-dashed border-slate-200 rounded-xl p-8 cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/10 transition-colors">
                  <input
                    type="file"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files?.[0]) {
                        setSelectedFile(e.target.files[0]);
                        setDescription(e.target.files[0].name);
                      }
                    }}
                  />
                  <CloudArrowUpIcon className="w-10 h-10 text-indigo-300 mx-auto mb-2" />
                  {selectedFile ? (
                    <div className="text-indigo-600 font-medium text-sm break-all">{selectedFile.name}</div>
                  ) : (
                    <span className="text-slate-400 text-xs font-bold uppercase tracking-wide">Click para seleccionar archivo</span>
                  )}
                </label>

                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 block">Descripción / Nombre</label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                    placeholder="Ej. Guía de Despacho, Informe Técnico..."
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1 px-4 py-3 bg-slate-100 text-slate-600 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-slate-200 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || isUploading}
                  className="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Subiendo...' : 'Adjuntar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentAttachments;