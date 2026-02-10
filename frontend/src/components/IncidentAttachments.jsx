import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PaperClipIcon,
  TrashIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  CalendarIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';

const IncidentAttachments = ({ incidentId, incidentCode }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [dragActive, setDragActive] = useState(false);
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

      const response = await api.post(
        `/documents/upload-attachment/`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
      showSuccess('Protocol Attached Successfully');
      setShowUploadModal(false);
      setSelectedFile(null);
      setDescription('');
      setIsPublic(false);
      setIsUploading(false);
    },
    onError: () => {
      showError('Transmission Failure: Could not attach document');
      setIsUploading(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (attachmentId) => {
      await api.delete(`/documents/attachments/incident/${incidentId}/${attachmentId}/delete/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
      showSuccess('Archive Entry Deleted');
    },
    onError: () => showError('Purge command failed'),
  });

  const handleView = useCallback(async (attachment) => {
    try {
      const response = await api.get(
        `/documents/attachments/incident/${incidentId}/${attachment.id}/download/`,
        { responseType: 'blob' }
      );
      const extension = attachment.filename.split('.').pop()?.toLowerCase();
      const mimeTypes = {
        jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif',
        pdf: 'application/pdf', doc: 'application/msword', docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        xls: 'application/vnd.ms-excel', xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        txt: 'text/plain',
      };
      const mimeType = mimeTypes[extension] || 'application/octet-stream';
      const blob = new Blob([response.data], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => window.URL.revokeObjectURL(url), 60000);
    } catch (err) {
      showError('Visual Retrieval Error');
    }
  }, [incidentId, showError]);

  const handleDownload = useCallback(async (attachment) => {
    try {
      const response = await api.get(
        `/documents/attachments/incident/${incidentId}/${attachment.id}/download/`,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = attachment.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      showError('Data Extraction Failure');
    }
  }, [incidentId, showError]);

  const handleDelete = useCallback((attachment) => {
    if (window.confirm(`Initiate purge protocol for "${attachment.filename}"?`)) {
      deleteMutation.mutate(attachment.id);
    }
  }, [deleteMutation]);

  const handleUpload = useCallback(() => {
    if (!selectedFile) return;
    setIsUploading(true);
    uploadMutation.mutate({ file: selectedFile, description, isPublic });
  }, [selectedFile, description, isPublic, uploadMutation]);

  const handleDrag = (e) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setDescription(e.dataTransfer.files[0].name);
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return '0 KB';
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + ['B', 'KB', 'MB', 'GB'][i];
  };

  if (!incidentId) return null;

  return (
    <div className="bg-[#050a14]/60 border border-white/5 rounded-sm overflow-hidden">
      {/* Header Deck */}
      <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <PaperClipIcon className="h-5 w-5 text-purple-400 shadow-[0_0_8px_rgba(168,85,247,0.4)]" />
          <div>
            <h4 className="data-font text-[11px] font-black uppercase text-white tracking-widest">Archive_Vault</h4>
            <p className="data-font text-[8px] text-gray-600 uppercase tracking-tighter">{attachments.length} Record(s) Linked</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => refetch()} className="p-2 text-gray-500 hover:text-white transition-colors">
            <ArrowPathIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="tactical-btn py-2 px-4 flex items-center gap-2"
          >
            <CloudArrowUpIcon className="h-4 w-4" />
            <span className="data-font text-[9px] font-black uppercase">Archive_Store</span>
          </button>
        </div>
      </div>

      {/* Archive Grid */}
      <div className="divide-y divide-white/5 bg-black/20">
        {isLoading ? (
          <div className="p-10 flex flex-col items-center justify-center space-y-4">
            <div className="w-8 h-8 border-2 border-purple-500/20 border-t-purple-500 animate-spin rounded-full"></div>
            <p className="data-font text-[8px] text-purple-400 uppercase animate-pulse">Scanning Vault...</p>
          </div>
        ) : attachments.length === 0 ? (
          <div className="p-12 text-center opacity-40">
            <DocumentTextIcon className="h-10 w-10 text-gray-600 mx-auto mb-4" />
            <p className="data-font text-[10px] text-gray-500 uppercase tracking-widest">Encryption Buffer Empty</p>
          </div>
        ) : (
          attachments.map((doc) => (
            <div key={doc.id} className="p-5 hover:bg-white/[0.02] flex items-center justify-between group transition-colors">
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="w-10 h-10 bg-white/5 border border-white/5 rounded-xs flex items-center justify-center group-hover:border-purple-500/30 transition-all">
                  <DocumentTextIcon className="w-5 h-5 text-gray-500 transition-colors group-hover:text-white" />
                </div>
                <div className="min-w-0">
                  <p className="data-font text-[11px] font-black text-white uppercase truncate tracking-tight">
                    {doc.description || doc.filename}
                  </p>
                  <div className="flex items-center gap-4 mt-1 opacity-60">
                    <span className="data-font text-[8px] text-gray-500 flex items-center gap-1 uppercase">
                      <CalendarIcon className="h-2.5 w-2.5" /> {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                    <span className="data-font text-[8px] text-gray-500 flex items-center gap-1 uppercase">
                      <UserIcon className="h-2.5 w-2.5" /> ID:{doc.created_by?.slice(0, 8) || 'SYS'}
                    </span>
                    <span className="data-font text-[8px] text-purple-400 uppercase font-black">{formatSize(doc.size)}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1 ml-4 opacity-20 group-hover:opacity-100 transition-opacity">
                <button onClick={() => handleView(doc)} className="p-2 text-gray-500 hover:text-cyan-400 transition-colors" title="View_Data">
                  <EyeIcon className="h-4 w-4" />
                </button>
                <button onClick={() => handleDownload(doc)} className="p-2 text-gray-500 hover:text-purple-400 transition-colors" title="Extract_File">
                  <ArrowDownTrayIcon className="h-4 w-4" />
                </button>
                <button onClick={() => handleDelete(doc)} className="p-2 text-gray-500 hover:text-rose-500 transition-colors" title="Purge_Entry">
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Tactical Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-[#050a14]/95 backdrop-blur-xl flex items-center justify-center z-[100] p-4">
          <div className="glass-panel max-w-md w-full border border-purple-500/20 overflow-hidden relative">
            <div className="absolute inset-0 scanline opacity-5"></div>
            <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
              <h5 className="data-font text-xs font-black uppercase text-white italic tracking-[0.2em]">Initiate_Store_Protocol</h5>
              <button onClick={() => setShowUploadModal(false)} className="text-gray-500 hover:text-white"><XMarkIcon className="h-5 w-5" /></button>
            </div>

            <div className="p-6 space-y-6">
              <div
                className={`border border-dashed p-10 text-center transition-all ${dragActive ? 'border-purple-500 bg-purple-500/10' : 'border-white/10 bg-white/[0.02]'}`}
                onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
              >
                {selectedFile ? (
                  <div className="space-y-3">
                    <CheckCircleIcon className="h-8 w-8 text-emerald-500 mx-auto" />
                    <p className="data-font text-[10px] text-white uppercase font-black">{selectedFile.name}</p>
                    <p className="data-font text-[8px] text-gray-500 uppercase">{formatSize(selectedFile.size)}</p>
                    <button onClick={() => setSelectedFile(null)} className="data-font text-[8px] text-rose-500 hover:underline uppercase tracking-widest font-black">De_Link_File</button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <CloudArrowUpIcon className="h-8 w-8 text-gray-700 mx-auto" />
                    <p className="data-font text-[9px] text-gray-600 uppercase tracking-widest">Link or Signal Archive Entry</p>
                    <input type="file" onChange={(e) => { setSelectedFile(e.target.files[0]); setDescription(e.target.files[0]?.name || ''); }} className="hidden" id="internal-upload" />
                    <label htmlFor="internal-upload" className="tactical-btn py-2 px-6 inline-block cursor-pointer data-font text-[9px] font-black">LINK_ENTRY</label>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <label className="data-font text-[8px] text-gray-600 uppercase tracking-widest">Metadata_Label</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-[#0a0f1d] border border-white/10 rounded-xs px-4 py-3 data-font text-xs text-white"
                  placeholder="ARCHIVE_LABEL_REQUIRED"
                />
              </div>

              <div className="flex items-center gap-3 bg-white/5 p-3 border border-white/5">
                <input type="checkbox" checked={isPublic} onChange={(e) => setIsPublic(e.target.checked)} className="checkbox-futuristic" id="pub-check" />
                <label htmlFor="pub-check" className="data-font text-[9px] text-gray-500 uppercase tracking-widest cursor-pointer">Unrestricted_Access_Protocol</label>
              </div>
            </div>

            <div className="p-6 bg-black/40 border-t border-white/5 flex gap-3">
              <button onClick={() => setShowUploadModal(false)} className="flex-1 tactical-btn py-4 data-font text-[10px] font-black uppercase">Abort</button>
              <button
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                className="flex-1 tactical-btn-active py-4 data-font text-[10px] font-black uppercase"
              >
                {isUploading ? 'SYNCING...' : 'COMMIT_ATTACH'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentAttachments;