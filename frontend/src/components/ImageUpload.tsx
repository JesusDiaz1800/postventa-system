import React, { useState, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNotifications } from '../hooks/useNotifications';
import { PhotoIcon, XMarkIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline';

const ImageUpload = ({ incidentId, onUploadSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (formData) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/incidents/${incidentId}/images/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al subir imagen');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      showSuccess('Imagen subida exitosamente');
      queryClient.invalidateQueries(['incident-images', incidentId]);
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
    },
    onError: (error) => {
      showError('Error al subir imagen: ' + error.message);
    },
  });

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    
    // Validar archivos
    const validFiles = files.filter(file => {
      const maxSize = 10 * 1024 * 1024; // 10MB
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      
      if (file.size > maxSize) {
        showError(`El archivo ${file.name} es demasiado grande. Máximo 10MB.`);
        return false;
      }
      
      if (!allowedTypes.includes(file.type)) {
        showError(`El archivo ${file.name} no es un tipo de imagen válido.`);
        return false;
      }
      
      return true;
    });

    if (validFiles.length === 0) return;

    // Crear previews
    const newPreviews = validFiles.map(file => ({
      file,
      id: Date.now() + Math.random(),
      preview: URL.createObjectURL(file)
    }));

    setSelectedFiles(prev => [...prev, ...validFiles]);
    setPreviews(prev => [...prev, ...newPreviews]);
  };

  const removeFile = (index) => {
    const fileToRemove = selectedFiles[index];
    const previewToRemove = previews[index];
    
    // Revocar URL del preview
    URL.revokeObjectURL(previewToRemove.preview);
    
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    
    try {
      // Subir archivos uno por uno
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append('image', file);
        
        await uploadMutation.mutateAsync(formData);
      }
      
      // Limpiar después de subir todos
      setSelectedFiles([]);
      setPreviews([]);
      
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const clearAll = () => {
    // Revocar todas las URLs
    previews.forEach(preview => URL.revokeObjectURL(preview.preview));
    
    setSelectedFiles([]);
    setPreviews([]);
  };

  return (
    <div className="space-y-4">
      {/* Botón de selección */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PhotoIcon className="h-4 w-4 mr-2" />
          Seleccionar Imágenes
        </button>
        
        {selectedFiles.length > 0 && (
          <button
            onClick={clearAll}
            className="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <XMarkIcon className="h-4 w-4 mr-2" />
            Limpiar Todo
          </button>
        )}
      </div>

      {/* Input oculto */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Previews */}
      {previews.length > 0 && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {previews.map((preview, index) => (
              <div key={preview.id} className="relative group">
                <div className="aspect-w-16 aspect-h-12 bg-gray-200 rounded-lg overflow-hidden">
                  <img
                    src={preview.preview}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
                <div className="mt-2">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {preview.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(preview.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Botones de acción */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              {selectedFiles.length} imagen{selectedFiles.length !== 1 ? 'es' : ''} seleccionada{selectedFiles.length !== 1 ? 's' : ''}
            </p>
            <div className="flex space-x-3">
              <button
                onClick={clearAll}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={uploadFiles}
                disabled={isUploading || uploadMutation.isPending}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading || uploadMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Subiendo...
                  </>
                ) : (
                  <>
                    <CloudArrowUpIcon className="h-4 w-4 mr-2" />
                    Subir Imágenes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
