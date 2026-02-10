import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { XMarkIcon, EyeIcon, DocumentIcon, PlusIcon, CameraIcon, BoltIcon } from '@heroicons/react/24/outline';
import { api } from '../services/api';
import ImageUpload from './ImageUpload';

const IncidentImages = ({ incident, onClose }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [showImageViewer, setShowImageViewer] = useState(false);
  const [showUploadSection, setShowUploadSection] = useState(false);

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

  return (
    <div className="fixed inset-0 bg-[#050a14]/90 backdrop-blur-md z-[60] flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-5xl max-h-[90vh] overflow-hidden border border-white/10 flex flex-col relative shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <div className="absolute inset-0 scanline opacity-5 pointer-events-none"></div>

        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
          <div className="flex items-center gap-4">
            <CameraIcon className="w-6 h-6 text-purple-400" />
            <div>
              <h3 className="text-white data-font text-xs font-black uppercase tracking-[0.3em] italic">Optical_Archive_Stream</h3>
              <p className="data-font text-[9px] text-gray-600 uppercase tracking-widest mt-0.5">Reference_ID: {incident.code}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowUploadSection(!showUploadSection)}
              className={`tactical-btn py-2 px-6 flex items-center gap-2 ${showUploadSection ? 'border-rose-500/30 text-rose-500' : ''}`}
            >
              {showUploadSection ? <XMarkIcon className="h-4 w-4" /> : <PlusIcon className="h-4 w-4" />}
              <span className="data-font text-[10px] uppercase font-black">{showUploadSection ? 'ABORT_UPLOAD' : 'LINK_OPTICAL_DATA'}</span>
            </button>
            <button onClick={onClose} className="p-2 text-gray-500 hover:text-white transition-colors">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar-purple">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <div className="w-10 h-10 border-2 border-purple-500/20 border-t-purple-500 animate-spin rounded-full"></div>
              <p className="data-font text-[10px] text-purple-400 uppercase tracking-widest animate-pulse">Initializing Data Buffer...</p>
            </div>
          ) : error ? (
            <div className="text-center py-20 border border-rose-500/20 bg-rose-500/5">
              <BoltIcon className="mx-auto h-12 w-12 text-rose-500 mb-4" />
              <h3 className="data-font text-white uppercase font-black tracking-widest">Protocol_Handshake_Failed</h3>
              <p className="data-font text-[10px] text-rose-400 uppercase mt-2">Could not retrieve optical stream from central server.</p>
            </div>
          ) : (
            <div className="space-y-10">
              {/* Upload Interface */}
              {showUploadSection && (
                <div className="bg-white/5 border border-purple-500/20 p-8 rounded-xs animate-scale-in relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-2"><BoltIcon className="w-4 h-4 text-purple-500/30" /></div>
                  <h4 className="data-font text-xs font-black text-white uppercase tracking-widest mb-6 italic">Secure_Upload_Portal</h4>
                  <ImageUpload
                    incidentId={incident.id}
                    onUploadSuccess={() => setShowUploadSection(false)}
                  />
                </div>
              )}

              {/* Data Grid */}
              <div>
                <div className="flex items-center gap-4 mb-8">
                  <div className="h-[1px] flex-1 bg-white/5"></div>
                  <h4 className="data-font text-[10px] text-gray-500 uppercase tracking-[0.4em] font-black">
                    Linked_Assets ({images.length})
                  </h4>
                  <div className="h-[1px] flex-1 bg-white/5"></div>
                </div>

                {images.length === 0 ? (
                  <div className="text-center py-20 opacity-30">
                    <DocumentIcon className="mx-auto h-12 w-12 text-gray-600 mb-4" />
                    <p className="data-font text-[10px] uppercase tracking-widest text-gray-500 font-black">Archive_Stream_Empty</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    {images.map((image) => (
                      <div
                        key={image.id}
                        className="group relative cursor-pointer"
                        onClick={() => handleImageClick(image)}
                      >
                        <div className="aspect-square bg-[#0a0f1d] border border-white/5 overflow-hidden relative group-hover:border-purple-500/50 transition-all duration-500">
                          <img
                            src={image.url || `/api/incidents/${incident.id}/images/${image.id}/view/`}
                            alt={image.filename || image.name}
                            className="w-full h-full object-cover grayscale opacity-60 group-hover:grayscale-0 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700"
                          />
                          <div className="absolute inset-0 bg-purple-500/0 group-hover:bg-purple-500/10 transition-colors pointer-events-none"></div>
                          <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 to-transparent translate-y-full group-hover:translate-y-0 transition-transform duration-300">
                            <p className="data-font text-[8px] text-white font-black uppercase truncate">{image.filename || image.name}</p>
                          </div>
                        </div>
                        <div className="mt-3 space-y-1">
                          <p className="data-font text-[9px] text-gray-500 uppercase tracking-tighter truncate group-hover:text-purple-400 transition-colors">
                            {image.filename || image.name}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="data-font text-[8px] text-gray-700 uppercase">
                              {image.file_size ? `${(image.file_size / 1024 / 1024).toFixed(1)} MB` : 'SIZE_NA'}
                            </span>
                            {image.uploaded_by && (
                              <span className="data-font text-[8px] text-gray-800 uppercase italic">
                                ID_{image.uploaded_by.username}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Global Optical Deep Dive */}
        {showImageViewer && selectedImage && (
          <div className="fixed inset-0 bg-[#050a14]/98 backdrop-blur-2xl flex items-center justify-center z-[100] animate-fade-in p-8">
            <div className="absolute inset-0 scanline opacity-10 pointer-events-none"></div>
            <div className="relative w-full h-full flex flex-col">
              {/* Deep Dive UI */}
              <div className="flex justify-between items-center mb-8 border-b border-white/5 pb-6">
                <div>
                  <h2 className="text-white data-font text-md font-black italic uppercase tracking-[0.5em]">Optical_Deep_Dive</h2>
                  <p className="data-font text-[9px] text-purple-400 uppercase tracking-widest mt-1">High_Resolution_Sync // {selectedImage.filename || selectedImage.name}</p>
                </div>
                <button onClick={closeImageViewer} className="tactical-btn p-4 group">
                  <XMarkIcon className="w-8 h-8 text-rose-500 transition-transform group-hover:scale-110" />
                </button>
              </div>

              <div className="flex-1 relative flex items-center justify-center bg-black/40 border border-white/5 overflow-hidden">
                <img
                  src={selectedImage.url || `/api/incidents/${incident.id}/images/${selectedImage.id}/view/`}
                  alt={selectedImage.filename || selectedImage.name}
                  className="max-w-full max-h-full object-contain shadow-[0_0_100px_rgba(168,85,247,0.1)]"
                />

                {/* HUD Overlays */}
                <div className="absolute top-8 left-8 p-4 border-l-2 border-t-2 border-purple-500/40 opacity-40">
                  <p className="data-font text-[10px] text-white">X: 1920 PX</p>
                  <p className="data-font text-[10px] text-white">Y: 1080 PX</p>
                </div>
                <div className="absolute bottom-8 right-8 p-4 border-r-2 border-b-2 border-purple-500/40 opacity-40">
                  <p className="data-font text-[10px] text-white text-right">SYNC_QUAL: 100%</p>
                  <p className="data-font text-[10px] text-white text-right">BIT_DEPTH: 24</p>
                </div>
              </div>

              <div className="mt-8 flex justify-between items-end">
                <div className="data-font text-[9px] text-gray-700 uppercase space-y-1">
                  <p>Filename: {selectedImage.filename || selectedImage.name}</p>
                  <p>Metadata: Integrated Central Grid</p>
                  <p>Security: Authorized Personnel Only</p>
                </div>
                <div className="flex gap-4">
                  <button onClick={closeImageViewer} className="tactical-btn py-4 px-12 data-font text-xs font-black tracking-widest">CLOSE_DEEP_DIVE</button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="p-6 border-t border-white/5 bg-black/40 flex justify-end">
          <button
            onClick={onClose}
            className="tactical-btn py-3 px-10 data-font text-[10px] font-black uppercase tracking-widest"
          >
            DISCONNECT_ARCHIVE
          </button>
        </div>
      </div>
    </div>
  );
};

export default IncidentImages;
