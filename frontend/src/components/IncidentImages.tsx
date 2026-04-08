import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { XMarkIcon, EyeIcon, PhotoIcon, PlusIcon, ArrowUpTrayIcon, TrashIcon } from '@heroicons/react/24/outline';
import { api } from '../services/api';
import ImageUpload from './ImageUpload';

const IncidentImages = ({ incident, onClose }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  const { data: imagesData, isLoading, refetch } = useQuery({
    queryKey: ['incident-images', incident.id],
    queryFn: () => api.get(`/incidents/${incident.id}/images/list/`),
    enabled: !!incident.id
  });

  const images = imagesData?.data?.images || [];

  const handleImageClick = (image) => {
    setSelectedImage(image);
  };

  const handleDelete = async (imageId, e) => {
    e.stopPropagation();
    if (confirm('¿Eliminar esta imagen?')) {
      try {
        await api.delete(`/incidents/${incident.id}/images/${imageId}/`);
        refetch();
      } catch (error) {
        console.error(error);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">{images.length} Archivos en Galería</p>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="text-[10px] font-black uppercase tracking-widest text-indigo-600 hover:text-indigo-800 flex items-center gap-2 bg-indigo-50 px-3 py-1.5 rounded-lg transition-colors"
        >
          {showUpload ? <XMarkIcon className="w-3 h-3" /> : <PlusIcon className="w-3 h-3" />}
          {showUpload ? 'Cancelar Carga' : 'Agregar Fotos'}
        </button>
      </div>

      {showUpload && (
        <div className="bg-slate-50 border border-slate-100 rounded-2xl p-6 animate-fade-in">
          <h4 className="text-xs font-black text-slate-700 uppercase tracking-widest mb-4">Subir Nueva Evidencia</h4>
          <ImageUpload
            incidentId={incident.id}
            onUploadSuccess={() => { setShowUpload(false); refetch(); }}
          />
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center p-8">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : images.length === 0 ? (
        <div className="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
          <PhotoIcon className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-xs text-slate-400 font-bold">No hay imágenes registradas</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {images.map(img => (
            <div key={img.id} className="group relative aspect-square bg-slate-100 rounded-xl overflow-hidden cursor-pointer shadow-sm hover:shadow-md transition-all" onClick={() => handleImageClick(img)}>
              <img
                src={img.url || `/api/incidents/${incident.id}/images/${img.id}/view/`}
                alt="Evidencia"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-slate-900/0 group-hover:bg-slate-900/10 transition-colors"></div>
              <button
                onClick={(e) => handleDelete(img.id, e)}
                className="absolute top-2 right-2 p-1.5 bg-white/90 text-rose-500 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shadow-sm hover:bg-rose-50"
              >
                <TrashIcon className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Lightbox / Modal de Visualización */}
      {selectedImage && (
        <div className="fixed inset-0 z-[10000] bg-slate-900/90 backdrop-blur-sm flex items-center justify-center p-4 md:p-10 animate-fade-in" onClick={() => setSelectedImage(null)}>
          <div className="relative max-w-5xl w-full max-h-full flex flex-col items-center" onClick={e => e.stopPropagation()}>
            <img
              src={selectedImage.url || `/api/incidents/${incident.id}/images/${selectedImage.id}/view/`}
              className="max-w-full max-h-[80vh] rounded-lg shadow-2xl"
            />
            <div className="mt-4 flex gap-4">
              <button onClick={() => setSelectedImage(null)} className="px-6 py-2 bg-white rounded-full text-xs font-black uppercase tracking-widest text-slate-900 hover:bg-slate-200 transition-colors shadow-lg">
                Cerrar Vista
              </button>
              <a
                href={selectedImage.url || `/api/incidents/${incident.id}/images/${selectedImage.id}/view/`}
                download
                target="_blank"
                rel="noreferrer"
                className="px-6 py-2 bg-indigo-600 rounded-full text-xs font-black uppercase tracking-widest text-white hover:bg-indigo-500 transition-colors shadow-lg flex items-center gap-2"
              >
                <ArrowUpTrayIcon className="w-4 h-4" /> Desgargar
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentImages;
