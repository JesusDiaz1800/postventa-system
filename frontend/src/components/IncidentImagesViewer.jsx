import React, { useState } from 'react';
import { PhotoIcon, XMarkIcon, ArrowDownTrayIcon, MagnifyingGlassPlusIcon } from '@heroicons/react/24/outline';

/**
 * IncidentImagesViewer - Un visualizador de galería premium para reportes técnicos.
 * @param {string} incidentId - El ID de la incidencia para construir las URLs.
 * @param {Array} images - Lista de objetos de imagen de la incidencia.
 */
const IncidentImagesViewer = ({ incidentId, images = [] }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  if (!images || images.length === 0) {
    return (
      <div className="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-8 text-center">
        <PhotoIcon className="h-10 w-10 text-slate-300 mx-auto mb-2" />
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Sin imágenes de referencia disponibles</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {images.map((img) => {
          // Intentar obtener URL del backend o usar el endpoint directo de visualización
          const imageUrl = img.url || `/api/incidents/${incidentId}/images/${img.id}/view/`;
          
          return (
            <div
              key={img.id}
              className="group relative aspect-square bg-white rounded-[1.5rem] overflow-hidden cursor-pointer shadow-sm hover:shadow-2xl transition-all duration-500 hover:-translate-y-1 border border-slate-100"
              onClick={() => setSelectedImage(img)}
            >
              <img
                src={imageUrl}
                alt="Evidencia técnica"
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                loading="lazy"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://via.placeholder.com/400x400?text=Error+Cargando+Imagen';
                }}
              />
              
              {/* Overlay Premium */}
              <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/20 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-end p-4">
                <div className="flex items-center gap-2 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                  <div className="p-1.5 bg-blue-600 rounded-lg shadow-lg shadow-blue-500/30">
                    <MagnifyingGlassPlusIcon className="h-3 w-3 text-white" />
                  </div>
                  <span className="text-[10px] text-white font-black uppercase tracking-widest">Ver Detalle</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Lightbox / Galería Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 z-[10000] bg-slate-900/95 backdrop-blur-xl flex items-center justify-center p-4 md:p-12 animate-fade-in"
          onClick={() => setSelectedImage(null)}
        >
          {/* Botón Cerrar Flotante */}
          <button 
            onClick={() => setSelectedImage(null)}
            className="absolute top-6 right-6 p-3 bg-white/10 hover:bg-white/20 text-white rounded-2xl backdrop-blur-md border border-white/10 transition-all z-10 hover:rotate-90"
            title="Cerrar (Esc)"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>

          <div className="relative max-w-5xl w-full max-h-full flex flex-col items-center" onClick={e => e.stopPropagation()}>
            <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-white/20 bg-slate-800 animate-scale-in">
              <img
                src={selectedImage.url || `/api/incidents/${incidentId}/images/${selectedImage.id}/view/`}
                alt="Ampliación de evidencia"
                className="max-w-full max-h-[75vh] object-contain"
              />
            </div>

            <div className="mt-8 flex flex-wrap justify-center gap-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
              <button 
                onClick={() => setSelectedImage(null)} 
                className="px-8 py-3.5 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 rounded-2xl text-[10px] font-black uppercase tracking-widest text-white transition-all"
              >
                Cerrar Galería
              </button>
              <a
                href={selectedImage.url || `/api/incidents/${incidentId}/images/${selectedImage.id}/view/`}
                download
                target="_blank"
                rel="noreferrer"
                className="px-8 py-3.5 bg-blue-600 hover:bg-blue-500 rounded-2xl text-[10px] font-black uppercase tracking-widest text-white transition-all shadow-xl shadow-blue-500/20 flex items-center gap-3 group"
              >
                <ArrowDownTrayIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" /> 
                Descargar Documentación
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentImagesViewer;
