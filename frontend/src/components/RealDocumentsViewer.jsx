import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  DocumentTextIcon, 
  EyeIcon, 
  ArrowDownTrayIcon, 
  TrashIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  FolderIcon,
  DocumentIcon
} from '@heroicons/react/24/outline';

const RealDocumentsViewer = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const queryClient = useQueryClient();

  // Fetch real documents
  const { data: documentsData, isLoading, error } = useQuery({
    queryKey: ['real-documents', filterType],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const url = filterType 
        ? `/api/documents/real-files/by-type/?type=${filterType}`
        : '/api/documents/real-files/';
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar documentos');
      }
      
      return response.json();
    },
  });

  // Fetch folder stats
  const { data: statsData } = useQuery({
    queryKey: ['folder-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/real-files/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar estadísticas');
      }
      
      return response.json();
    },
  });

  // Search documents
  const { data: searchData, isLoading: isSearching } = useQuery({
    queryKey: ['search-documents', searchQuery],
    queryFn: async () => {
      if (!searchQuery.trim()) return null;
      
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/real-files/search/?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Error en la búsqueda');
      }
      
      return response.json();
    },
    enabled: !!searchQuery.trim(),
  });

  // Delete document mutation
  const deleteDocumentMutation = useMutation({
    mutationFn: async (filename) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/real-files/${filename}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al eliminar documento');
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['real-documents']);
      queryClient.invalidateQueries(['folder-stats']);
      alert('✅ Documento eliminado exitosamente');
    },
    onError: (error) => {
      alert('Error al eliminar documento: ' + error.message);
    },
  });

  const handleViewDocument = (filename) => {
    const token = localStorage.getItem('access_token');
    const url = `/api/documents/real-files/${filename}/serve/`;
    
    // Open in new tab
    window.open(url, '_blank');
  };

  const handleDownloadDocument = (filename) => {
    const token = localStorage.getItem('access_token');
    const url = `/api/documents/real-files/${filename}/serve/`;
    
    // Create download link
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDeleteDocument = (filename) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar el archivo "${filename}"?`)) {
      deleteDocumentMutation.mutate(filename);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString('es-ES');
  };

  const openFileInExplorer = (filePath) => {
    // Copy file path to clipboard and show message
    navigator.clipboard.writeText(filePath).then(() => {
      alert(`✅ Ruta del archivo copiada al portapapeles:\n${filePath}\n\nPuedes pegarla en el explorador de Windows.`);
    }).catch(() => {
      // Fallback: show the path in an alert
      alert(`📁 Ruta del archivo:\n${filePath}\n\nCopia esta ruta y ábrela en el explorador de Windows.`);
    });
  };

  const openFileLocation = (filePath) => {
    // Get folder path and copy to clipboard
    const folderPath = filePath.substring(0, filePath.lastIndexOf('\\'));
    navigator.clipboard.writeText(folderPath).then(() => {
      alert(`✅ Ruta de la carpeta copiada al portapapeles:\n${folderPath}\n\nPuedes pegarla en la barra de direcciones del explorador de Windows.`);
    }).catch(() => {
      // Fallback: show the path in an alert
      alert(`📂 Ruta de la carpeta:\n${folderPath}\n\nCopia esta ruta y ábrela en el explorador de Windows.`);
    });
  };

  const getFileIcon = (extension) => {
    switch (extension) {
      case '.pdf':
        return <DocumentTextIcon className="h-6 w-6 text-red-500" />;
      case '.docx':
      case '.doc':
        return <DocumentTextIcon className="h-6 w-6 text-blue-500" />;
      case '.xlsx':
      case '.xls':
        return <DocumentTextIcon className="h-6 w-6 text-green-500" />;
      case '.jpg':
      case '.jpeg':
      case '.png':
      case '.gif':
        return <DocumentIcon className="h-6 w-6 text-purple-500" />;
      default:
        return <DocumentTextIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const files = searchQuery.trim() ? (searchData?.files || []) : (documentsData?.files || []);
  const stats = statsData?.stats;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error al cargar documentos: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with stats */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FolderIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Archivos reales en: {stats?.folder_path}</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Total de archivos</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_files}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Tamaño total</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_size_mb} MB</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">PDFs</p>
              <p className="text-2xl font-bold text-gray-900">{stats.type_counts['.pdf'] || 0}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Word</p>
              <p className="text-2xl font-bold text-gray-900">{(stats.type_counts['.docx'] || 0) + (stats.type_counts['.doc'] || 0)}</p>
            </div>
          </div>
        )}
      </div>

      {/* Search and filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar documentos por nombre..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los tipos</option>
              <option value="pdf">PDF</option>
              <option value="word">Word</option>
              <option value="excel">Excel</option>
              <option value="images">Imágenes</option>
              <option value="text">Texto</option>
            </select>
          </div>
        </div>
      </div>

      {/* Files list */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            {searchQuery.trim() ? `Resultados de búsqueda (${files.length})` : `Documentos (${files.length})`}
          </h3>
        </div>

        {files.length === 0 ? (
          <div className="p-8 text-center">
            <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchQuery.trim() ? 'No se encontraron documentos' : 'No hay documentos en la carpeta'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {files.map((file, index) => (
              <div key={index} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getFileIcon(file.extension)}
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{file.filename}</h4>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(file.size)} • {formatDate(file.modified_at)}
                      </p>
                      {file.incident_code && (
                        <p className="text-xs text-blue-600 font-medium">
                          📁 Incidencia: {file.incident_code}
                        </p>
                      )}
                      {file.preview && (
                        <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                          {file.preview.substring(0, 100)}...
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {file.can_view && (
                      <button
                        onClick={() => handleViewDocument(file.filename)}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Ver documento"
                      >
                        <EyeIcon className="h-5 w-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDownloadDocument(file.filename)}
                      className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                      title="Descargar documento"
                    >
                      <ArrowDownTrayIcon className="h-5 w-5" />
                    </button>
                    {file.file_path && (
                      <button
                        onClick={() => openFileInExplorer(file.file_path)}
                        className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                        title="Copiar ruta del archivo"
                      >
                        <FolderIcon className="h-5 w-5" />
                      </button>
                    )}
                    {file.file_path && (
                      <button
                        onClick={() => openFileLocation(file.file_path)}
                        className="p-2 text-gray-400 hover:text-indigo-600 transition-colors"
                        title="Copiar ruta de la carpeta"
                      >
                        <DocumentIcon className="h-5 w-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteDocument(file.filename)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="Eliminar documento"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RealDocumentsViewer;
