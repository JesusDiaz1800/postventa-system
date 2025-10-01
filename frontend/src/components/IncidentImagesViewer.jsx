import React, { useState } from 'react';
import { PhotoIcon, XMarkIcon, EyeIcon } from '@heroicons/react/24/outline';

const IncidentImagesViewer = ({ incidentId, images = [] }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openImageModal = (image) => {
    setSelectedImage(image);
    setIsModalOpen(true);
  };

  const closeImageModal = () => {
    setSelectedImage(null);
    setIsModalOpen(false);
  };

  if (!images || images.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-center text-gray-500">
          <PhotoIcon className="h-5 w-5 mr-2" />
          <span className="text-sm">No hay imágenes adjuntas</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <PhotoIcon className="h-5 w-5 mr-2" />
            Imágenes Adjuntas ({images.length})
          </h3>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((image, index) => (
            <div
              key={index}
              className="relative group cursor-pointer"
              onClick={() => openImageModal(image)}
            >
              <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                <div className="w-full h-full flex items-center justify-center">
                  <PhotoIcon className="h-12 w-12 text-gray-400" />
                </div>
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                  <EyeIcon className="h-6 w-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                </div>
              </div>
              <div className="mt-2">
                <p className="text-xs font-medium text-gray-900 truncate">
                  {image.filename}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {image.caption_ai || 'Sin descripción'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal para ver imagen */}
      {isModalOpen && selectedImage && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center p-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={closeImageModal}></div>
            
            <div className="relative bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedImage.filename}
                </h3>
                <button
                  onClick={closeImageModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="p-4">
                <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
                  <div className="w-full h-full flex items-center justify-center">
                    <PhotoIcon className="h-24 w-24 text-gray-400" />
                    <span className="ml-2 text-gray-500">Imagen no disponible</span>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Descripción:</label>
                    <p className="text-sm text-gray-900 mt-1">
                      {selectedImage.caption_ai || 'Sin descripción disponible'}
                    </p>
                  </div>
                  
                  {selectedImage.analysis_json && (
                    <div>
                      <label className="text-sm font-medium text-gray-700">Análisis de IA:</label>
                      <div className="mt-1 space-y-2">
                        {selectedImage.analysis_json.suggested_causes && (
                          <div>
                            <span className="text-xs font-medium text-gray-600">Causas sugeridas:</span>
                            <ul className="text-xs text-gray-700 mt-1 list-disc list-inside">
                              {selectedImage.analysis_json.suggested_causes.map((cause, idx) => (
                                <li key={idx}>{cause}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {selectedImage.ai_confidence && (
                          <div>
                            <span className="text-xs font-medium text-gray-600">Confianza:</span>
                            <span className="text-xs text-gray-700 ml-1">
                              {(selectedImage.ai_confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                    <div>
                      <span className="font-medium">Tamaño:</span> {(selectedImage.file_size / 1024 / 1024).toFixed(2)} MB
                    </div>
                    <div>
                      <span className="font-medium">Tipo:</span> {selectedImage.mime_type}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default IncidentImagesViewer;
