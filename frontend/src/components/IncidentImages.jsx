import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { XMarkIcon, EyeIcon, DocumentIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { api } from '../services/api';
import ImageUpload from './ImageUpload';

const IncidentImages = ({ incident, onClose }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [showImageViewer, setShowImageViewer] = useState(false);
  const [showUploadSection, setShowUploadSection] = useState(false);

  // Obtener imágenes reales del backend
  const { data: imagesData, isLoading, error } = useQuery({
    queryKey: ['incident-images', incident.id],
    queryFn: () => api.get(`/incidents/${incident.id}/images/list/`),
    enabled: !!incident.id
  });

  const images = imagesData?.data?.images || [];

  const handleImageClick = (image) => {
    setSelectedImage(image);
    setShowImageViewer(true);
  };

  const closeImageViewer = () => {
    setSelectedImage(null);
    setShowImageViewer(false);
  };

  const handleUploadSuccess = () => {
    setShowUploadSection(false);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-2/3 shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Imágenes Adjuntas - {incident.code}
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowUploadSection(!showUploadSection)}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              {showUploadSection ? 'Cancelar' : 'Subir Imágenes'}
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Cargando imágenes...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <DocumentIcon className="mx-auto h-12 w-12 text-red-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Error al cargar imágenes</h3>
            <p className="mt-1 text-sm text-gray-500">
              No se pudieron cargar las imágenes de esta incidencia.
            </p>
          </div>
        ) : images.length === 0 ? (
          <div className="text-center py-8">
            <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay imágenes</h3>
            <p className="mt-1 text-sm text-gray-500">
              No se han adjuntado imágenes a esta incidencia.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Sección de subida */}
            {showUploadSection && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Subir Nuevas Imágenes</h4>
                <ImageUpload 
                  incidentId={incident.id} 
                  onUploadSuccess={handleUploadSuccess}
                />
              </div>
            )}

            {/* Lista de imágenes existentes */}
            {images.length > 0 && (
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">
                  Imágenes Existentes ({images.length})
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {images.map((image) => (
                    <div
                      key={image.id}
                      className="relative group cursor-pointer"
                      onClick={() => handleImageClick(image)}
                    >
                      <div className="aspect-w-16 aspect-h-12 bg-gray-200 rounded-lg overflow-hidden">
                        <img
                          src={image.url || `/api/incidents/${incident.id}/images/${image.id}/view/`}
                          alt={image.filename || image.name}
                          className="w-full h-full object-cover group-hover:opacity-75 transition-opacity"
                        />
                      </div>
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
                        <EyeIcon className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                      <div className="mt-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {image.filename || image.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {image.file_size ? `${(image.file_size / 1024 / 1024).toFixed(1)} MB` : image.size}
                        </p>
                        {image.uploaded_by && (
                          <p className="text-xs text-gray-400">
                            Subido por: {image.uploaded_by.username}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Visor de imagen */}
        {showImageViewer && selectedImage && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60">
            <div className="relative max-w-4xl max-h-full p-4">
              <button
                onClick={closeImageViewer}
                className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
              >
                <XMarkIcon className="h-8 w-8" />
              </button>
              <img
                src={selectedImage.url || `/api/incidents/${incident.id}/images/${selectedImage.id}/view/`}
                alt={selectedImage.filename || selectedImage.name}
                className="max-w-full max-h-full object-contain"
              />
              <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-50 text-white p-3 rounded">
                <p className="font-medium">{selectedImage.filename || selectedImage.name}</p>
                <p className="text-sm opacity-75">
                  {selectedImage.file_size ? `${(selectedImage.file_size / 1024 / 1024).toFixed(1)} MB` : selectedImage.size}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default IncidentImages;
