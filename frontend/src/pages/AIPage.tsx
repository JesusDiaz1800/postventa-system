import { useState, useRef, useEffect } from 'react';
import {
  SparklesIcon,
  PaperAirplaneIcon,
  PhotoIcon,
  XMarkIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  ChartBarIcon,
  TrashIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  LightBulbIcon,
  MagnifyingGlassIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { useAIChat, ChatMessage } from '../hooks/useAIChat';

// ============================================================================
// COMPONENT: Chat Message Bubble
// ============================================================================
const MessageBubble = ({ message, onOpenReport, onCopy }: { 
  message: ChatMessage; 
  onOpenReport: (data: any) => void;
  onCopy: (text: string) => void;
}) => {
  const isUser = message.role === 'user';

  // Simple Markdown Parser
  const renderContent = (text: string) => {
    return text.split('\n').map((line, i) => {
      // Headers
      if (line.startsWith('### ')) return <h3 key={i} className="text-lg font-bold text-indigo-200 mt-4 mb-2">{line.replace('### ', '')}</h3>;
      if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold text-indigo-300 mt-6 mb-3">{line.replace('## ', '')}</h2>;

      // Bullet points
      if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
        return (
          <div key={i} className="flex gap-2 ml-4 mb-1">
            <span className="text-indigo-400 mt-1.5 font-bold">•</span>
            <span dangerouslySetInnerHTML={{ __html: formatBold(line.replace(/^[-•]\s+/, '')) }} />
          </div>
        );
      }

      // Numbered lists
      if (/^\d+\.\s/.test(line)) {
        return (
          <div key={i} className="flex gap-2 ml-4 mb-1">
            <span className="text-blue-400 font-mono text-sm mt-0.5 font-bold">{line.match(/^\d+\./)?.[0]}</span>
            <span dangerouslySetInnerHTML={{ __html: formatBold(line.replace(/^\d+\.\s+/, '')) }} />
          </div>
        );
      }

      // Tables (Basic support)
      if (line.includes('|') && line.split('|').length > 2) {
        const cells = line.split('|').filter(c => c.trim() !== '').map(c => c.trim());
        return (
          <div key={i} className="overflow-x-auto my-4 rounded-xl border border-white/10 bg-black/20">
            <table className="w-full text-xs text-left border-collapse">
              <tbody>
                <tr>
                  {cells.map((cell, idx) => (
                    <td key={idx} className="p-3 border-r border-white/5 last:border-0" dangerouslySetInnerHTML={{ __html: formatBold(cell) }} />
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        );
      }

      return <p key={i} className="mb-3 leading-relaxed text-slate-300/90" dangerouslySetInnerHTML={{ __html: formatBold(line) }} />;
    });
  };

  const formatBold = (text: string) => {
    return text.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="bg-black/40 px-1.5 py-0.5 rounded text-amber-300 font-mono text-xs border border-white/5 whitespace-nowrap">$1</code>');
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-8 group animate-fadeIn`}>
      <div className={`relative max-w-[90%] md:max-w-[85%] rounded-[1.5rem] p-5 md:p-6 shadow-2xl border transition-all duration-500 ${isUser
        ? 'bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 border-white/10 text-white rounded-br-none'
        : 'bg-[#151B28]/60 backdrop-blur-md border-white/5 text-slate-200 rounded-bl-none hover:border-white/10 shadow-indigo-500/5'
        }`}>

        {/* Glow effect for AI messages */}
        {!isUser && (
          <div className="absolute -inset-px bg-gradient-to-br from-indigo-500/20 to-transparent rounded-[2.5rem] blur opacity-50 -z-10 group-hover:opacity-100 transition-opacity" />
        )}

        {/* Header (Role & Time) */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-5">
            <div className="bg-indigo-500/20 p-1.5 rounded-lg border border-indigo-500/30">
              <CpuChipIcon className="w-4 h-4 text-indigo-400" />
            </div>
            <span className="text-[10px] uppercase tracking-[0.2em] font-black text-indigo-400">Asistente IA Industrial</span>
            <span className="ml-auto font-mono text-[9px] text-white/20">{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}

        {/* Image Previews (User) */}
        {message.metadata?.imagePreviews && message.metadata.imagePreviews.length > 0 && (
          <div className="grid grid-cols-2 gap-3 mb-6">
            {message.metadata.imagePreviews.map((preview, idx) => (
              <div key={idx} className="relative aspect-[16/10] rounded-2xl overflow-hidden border border-white/10 group/img">
                <img src={preview} alt={`Adjunto ${idx + 1}`} className="w-full h-full object-cover transition-transform duration-700 group-hover/img:scale-110" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
              </div>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="prose prose-invert prose-sm max-w-none">
          {renderContent(message.content)}
        </div>

        {/* Assistant Actions/Metadata */}
        {!isUser && (
          <div className="mt-8 flex flex-wrap gap-3 items-center pt-6 border-t border-white/5">
            {message.metadata?.confidence && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/40 border border-white/5">
                <ShieldCheckIcon className="w-3 h-3 text-emerald-400" />
                <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">
                  Fiabilidad {Math.round(message.metadata.confidence * 100)}%
                </span>
              </div>
            )}

            {/* Source Tags */}
            {message.metadata?.sources && message.metadata.sources.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {message.metadata.sources.map((source, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[9px] font-bold uppercase tracking-wider">
                    <DocumentTextIcon className="w-3 h-3" />
                    {source.replace(' (NotebookLM)', '')}
                  </div>
                ))}
              </div>
            )}

            <div className="flex-1" />

            <button 
              onClick={() => onCopy(message.content)}
              className="p-2 hover:bg-white/5 rounded-xl text-white/40 hover:text-white transition-all flex items-center gap-2 text-[10px] uppercase font-bold tracking-widest"
              title="Copiar respuesta"
            >
              <ArrowPathIcon className="w-4 h-4" /> 
              Copiar
            </button>

            {/* Report Generator / Viewer Actions */}
            {message.metadata?.analysisData && (
              <button
                onClick={() => onOpenReport(message.metadata?.analysisData)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 hover:bg-indigo-500 hover:text-white transition-all text-[10px] font-black uppercase tracking-widest"
              >
                <ChartBarIcon className="w-4 h-4" />
                Ver Diagnóstico
              </button>
            )}

            {message.metadata?.reportHtml && (
              <button
                onClick={() => {
                  const win = window.open('', '_blank');
                  win?.document.write(message.metadata!.reportHtml!);
                }}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 hover:bg-blue-500 hover:text-white transition-all text-[10px] font-black uppercase tracking-widest"
              >
                <DocumentTextIcon className="w-4 h-4" />
                Abrir Reporte
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// COMPONENT: Diagnosis Panel (Right Side)
// ============================================================================
const DiagnosisPanel = ({ data, onClose, onGenerateReport, isGeneratingReport }: {
  data: any,
  onClose: () => void,
  onGenerateReport: () => void,
  isGeneratingReport: boolean
}) => {
  if (!data) return null;

  return (
    <div className="absolute inset-y-0 right-0 w-full md:w-[600px] bg-[#05080F]/90 backdrop-blur-2xl border-l border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] p-8 overflow-y-auto transform transition-transform z-30 animate-slideInRight">
      <div className="flex items-center justify-between mb-10">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">
            Análisis <span className="text-indigo-500">Técnico</span>
          </h2>
          <p className="text-white/30 text-xs font-bold uppercase tracking-[0.2em] mt-1">SISTEMA DE ASISTENCIA INDUSTRIAL</p>
        </div>
        <button onClick={onClose} className="p-2.5 hover:bg-white/5 rounded-full transition-colors text-white/50 hover:text-white border border-transparent hover:border-white/10">
          <XMarkIcon className="w-6 h-6" />
        </button>
      </div>

      <div className="space-y-8">
        {/* Observations */}
        <div className="bg-[#0B0F19] rounded-3xl p-6 border border-white/5">
          <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
            <MagnifyingGlassIcon className="w-4 h-4" /> Resumen de Hallazgos
          </h3>
          <p className="text-slate-300 text-sm leading-relaxed font-medium">{data.observations || "Esperando datos de análisis..."}</p>
        </div>

        {/* Causes */}
        <div className="grid grid-cols-1 gap-6">
          <div className="bg-[#0B0F19] rounded-3xl p-6 border border-white/5">
            <h3 className="text-[10px] font-black text-rose-500 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
              <ExclamationTriangleIcon className="w-4 h-4" /> Causas Probables
            </h3>
            <div className="space-y-3">
              {data.possible_causes?.map((cause: string, i: number) => (
                <div key={i} className="flex gap-4 items-start bg-rose-500/5 p-4 rounded-2xl border border-rose-500/10 group">
                  <div className="w-6 h-6 rounded-lg bg-rose-500/20 flex items-center justify-center text-rose-500 text-xs font-black shrink-0">
                    {i + 1}
                  </div>
                  <p className="text-slate-300 text-sm font-medium">{cause}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#0B0F19] rounded-3xl p-6 border border-white/5">
            <h3 className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
              <LightBulbIcon className="w-4 h-4" /> Recomendaciones
            </h3>
            <div className="space-y-3">
              {data.recommendations?.map((rec: string, i: number) => (
                <div key={i} className="flex gap-4 items-start bg-emerald-500/5 p-4 rounded-2xl border border-emerald-500/10">
                  <div className="w-6 h-6 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-500 text-xs font-black shrink-0">
                    <CheckCircleIcon className="w-4 h-4" />
                  </div>
                  <p className="text-slate-300 text-sm font-medium">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action Button Area */}
        <div className="pt-10">
          <button
            onClick={onGenerateReport}
            disabled={isGeneratingReport}
            className="w-full py-5 rounded-2xl bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-600 bg-[length:200%_auto] hover:bg-right transition-all duration-500 text-white font-black uppercase tracking-[0.2em] shadow-2xl shadow-indigo-500/30 disabled:opacity-50 flex items-center justify-center gap-4"
          >
            {isGeneratingReport ? (
              <ArrowPathIcon className="w-6 h-6 animate-spin" />
            ) : (
              <DocumentTextIcon className="w-6 h-6" />
            )}
            {isGeneratingReport ? 'Procesando Documento...' : 'Generar Informe PDF Oficial'}
          </button>
          <div className="mt-4 flex items-center justify-center gap-2 text-white/20 uppercase text-[9px] font-black tracking-widest">
            <ShieldCheckIcon className="w-3 h-3" />
            Firmado por el sistema inteligente de postventa
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN PAGE
// ============================================================================
export default function AIPage() {
  const { 
    messages, 
    isLoading, 
    error, 
    sendMessage, 
    generateReport, 
    clearChat, 
    lastAnalysisData, 
    setLastAnalysisData,
    provider,
    setProvider
  } = useAIChat();
  const [inputValue, setInputValue] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [filePreviews, setFilePreviews] = useState<string[]>([]);
  const [showPanel, setShowPanel] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      const combined = [...selectedFiles, ...newFiles].slice(0, 5);
      setSelectedFiles(combined);

      Promise.all(combined.map(f => new Promise<string>(r => {
        const reader = new FileReader();
        reader.onload = (ev) => r(ev.target!.result as string);
        reader.readAsDataURL(f);
      }))).then(previews => setFilePreviews(previews));
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setFilePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    // Success feedback could be added here
  };

  const handleSend = async () => {
    if (!inputValue.trim() && selectedFiles.length === 0) return;
    await sendMessage(inputValue, selectedFiles);
    setInputValue('');
    setSelectedFiles([]);
    setFilePreviews([]);
    if (selectedFiles.length > 0) setShowPanel(true);
  };

  useEffect(() => {
    if (lastAnalysisData) setShowPanel(true);
  }, [lastAnalysisData]);

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-[#0B0F19] text-white overflow-hidden font-sans selection:bg-indigo-500/30">

      {/* SIDEBAR (Mini) */}
      <div className="w-20 md:w-64 bg-[#05080F] border-r border-white/5 flex flex-col items-center md:items-stretch py-5 md:px-5 z-10 transition-all">
        <div className="mb-0 md:mb-8 flex flex-col items-center md:flex-row md:items-center md:gap-4 md:px-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/40 shrink-0">
            <SparklesIcon className="w-7 h-7 text-white" />
          </div>
          <div className="hidden md:block">
            <h1 className="font-black text-xl leading-none tracking-tighter uppercase">Asistente <span className="text-indigo-500">IA</span></h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/30 text-[8px] font-black text-emerald-400 uppercase tracking-widest animate-pulse">
                Sincronizado v1.0
              </span>
            </div>
          </div>
        </div>

        {/* AI Selector Toggle */}
        <div className="mb-6 p-1.5 bg-black/40 backdrop-blur-md rounded-2xl border border-white/5 flex gap-1">
          <button
            onClick={() => setProvider('Gemini')}
            className={`flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 ${
              provider === 'Gemini' 
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 font-black' 
              : 'text-white/40 hover:text-white/60 font-bold'
            }`}
          >
            <SparklesIcon className={`w-4 h-4 ${provider === 'Gemini' ? 'animate-pulse' : ''}`} />
            <span className="text-[10px] uppercase tracking-widest">Nube</span>
          </button>
          <button
            onClick={() => setProvider('Ollama')}
            className={`flex-1 py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 ${
              provider === 'Ollama' 
              ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20 font-black' 
              : 'text-white/40 hover:text-white/60 font-bold'
            }`}
          >
            <CpuChipIcon className={`w-4 h-4 ${provider === 'Ollama' ? 'animate-bounce' : ''}`} />
            <span className="text-[10px] uppercase tracking-widest">Local</span>
          </button>
        </div>

        <button
          onClick={clearChat}
          className="md:w-full bg-white/5 hover:bg-white/10 text-white/60 hover:text-white p-3 md:px-4 md:py-3.5 rounded-xl flex items-center justify-center md:justify-start gap-3 transition-all border border-white/5 group mb-6 shadow-inner shadow-white/5"
        >
          <ArrowPathIcon className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
          <span className="hidden md:inline font-bold text-[10px] uppercase tracking-widest">Nueva Consulta</span>
        </button>

        <div className="flex-1 overflow-y-auto w-full space-y-3 custom-scrollbar">
          <div className="hidden md:block px-2 text-[9px] font-black uppercase tracking-[0.2em] text-white/20 mb-4">Historial de Análisis</div>
          <div className="hidden md:block px-4 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-bold uppercase tracking-widest text-indigo-300">
            Sesión de Diagnóstico Actual
          </div>
        </div>

        {/* Quick Help */}
        <div className="hidden md:block p-4 rounded-2xl bg-white/[0.02] border border-white/5 mt-8">
          <p className="text-[9px] leading-relaxed text-white/20 font-bold uppercase tracking-widest">
            Utiliza este asistente para análisis técnico de fallas, revisión de normas o dudas sobre la arquitectura del sistema.
          </p>
        </div>
      </div>

      {/* MAIN CHAT AREA */}
      <div className="flex-1 flex flex-col relative w-full bg-[radial-gradient(circle_at_50%_0%,rgba(79,70,229,0.05)_0%,transparent_50%)]">

        {/* Top Header Information */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-white/5 bg-[#0B0F19]/50 backdrop-blur-md">
          <h1 className="font-black text-xs uppercase tracking-widest">Asistente IA</h1>
          <button onClick={clearChat} className="p-2 bg-white/5 rounded-lg">
            <ArrowPathIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 md:px-8 md:py-6 scroll-smooth custom-scrollbar">
          <div className="w-full max-w-full mx-auto">
            {messages.length === 0 && (
              <div className="h-[50vh] flex flex-col items-center justify-center text-center animate-fadeIn">
                <div className="w-20 h-20 rounded-[2rem] bg-indigo-600/10 flex items-center justify-center border border-indigo-600/20 mb-8 relative">
                  <SparklesIcon className="w-10 h-10 text-indigo-400" />
                  <div className="absolute -inset-4 bg-indigo-500/10 rounded-full blur-2xl animate-pulse" />
                </div>
                <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-4">
                  ¿Cómo puedo <span className="text-indigo-500">ayudarte</span> hoy?
                </h2>
                <p className="text-white/40 max-w-md text-sm leading-relaxed font-medium">
                  Sube imágenes de fallas técnicas o consulta sobre procedimientos de instalación y normativas industriales.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-10">
                  {['¿Cuáles son los pasos para soldadura por polifusión?', 'Analiza estas grietas en la tubería de HDPE'].map((hint, i) => (
                    <button
                      key={i}
                      onClick={() => setInputValue(hint)}
                      className="px-5 py-3 rounded-2xl bg-white/5 border border-white/10 text-xs font-bold text-white/60 hover:border-indigo-500/30 hover:bg-indigo-500/5 hover:text-white transition-all text-left"
                    >
                      {hint}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                onOpenReport={(data) => {
                  setLastAnalysisData(data);
                  setShowPanel(true);
                }}
                onCopy={handleCopy}
              />
            ))}

            {isLoading && (
              <div className="flex justify-start mb-8 animate-fadeIn">
                <div className="bg-[#151B28]/60 backdrop-blur-md border border-white/5 rounded-[2rem] p-8 flex items-center gap-6 shadow-2xl shadow-indigo-500/5">
                  <div className="relative">
                    <ArrowPathIcon className="w-6 h-6 animate-spin text-indigo-400" />
                    <div className="absolute inset-0 blur-lg bg-indigo-500/50 animate-pulse" />
                  </div>
                  <span className="text-xs font-black uppercase tracking-[0.2em] text-indigo-200">
                    Procesando <span className="animate-pulse">...</span>
                  </span>
                </div>
              </div>
            )}

            {error && (
              <div className="flex justify-center mb-10 animate-shake">
                <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-[1.5rem] text-xs font-bold uppercase tracking-widest flex items-center gap-4 shadow-xl shadow-red-500/5">
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                  {error}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} className="h-10" />
          </div>
        </div>

        {/* INPUT AREA */}
        <div className="px-4 py-4 md:px-8 md:pb-8 z-20">
          <div className="w-full max-w-full mx-auto">
            {/* File Previews */}
            {filePreviews.length > 0 && (
              <div className="flex gap-4 mb-6 overflow-x-auto pb-4 scrollbar-hide">
                {filePreviews.map((src, i) => (
                  <div key={i} className="relative w-28 h-28 rounded-2xl overflow-hidden border-2 border-indigo-500/30 group shadow-2xl animate-scaleIn">
                    <img src={src} alt="Upload" className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button
                        onClick={() => removeFile(i)}
                        className="p-2 bg-red-500 rounded-xl text-white hover:bg-red-600 transition-all scale-75 group-hover:scale-100"
                      >
                        <TrashIcon className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                ))}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-28 h-28 border-2 border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center text-white/20 hover:border-indigo-500/40 hover:text-indigo-500 transition-all bg-white/[0.02]"
                >
                  <PhotoIcon className="w-6 h-6 mb-1" />
                  <span className="text-[9px] font-black uppercase tracking-widest">Añadir</span>
                </button>
              </div>
            )}

            <div className={`relative transition-all duration-500 ${inputValue.length > 30 ? 'scale-[1.02]' : 'scale-100'}`}>
              {/* Visual glow on focus */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-[2.5rem] blur opacity-0 transition-opacity duration-500 group-within:opacity-20" />

              <div className="relative flex gap-4 items-end bg-[#151B28] p-3 rounded-[2.5rem] border border-white/10 shadow-2xl focus-within:border-indigo-500/50 transition-all group">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className={`p-5 rounded-[2rem] transition-all border shrink-0 ${selectedFiles.length > 0 ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-900/40' : 'bg-white/5 border-white/5 text-white/50 hover:bg-white/10 hover:text-white'}`}
                >
                  <PhotoIcon className="w-7 h-7" />
                </button>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={handleFileSelect}
                />

                <div className="flex-1 min-h-[64px] flex items-center">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                    placeholder="Consulta sobre incidencias, normas o arquitectura..."
                    className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-white/20 py-4 px-4 max-h-40 resize-none font-bold text-lg leading-snug"
                  />
                </div>

                <button
                  onClick={handleSend}
                  disabled={isLoading || (!inputValue.trim() && selectedFiles.length === 0)}
                  className="p-4 rounded-[1.5rem] bg-indigo-600 text-white shadow-xl shadow-indigo-900/40 hover:bg-indigo-500 disabled:opacity-25 disabled:shadow-none disabled:grayscale transition-all active:scale-95 group"
                >
                  <PaperAirplaneIcon className="w-6 h-6 -rotate-45 translate-x-1 -translate-y-1 group-hover:translate-x-1.5 group-hover:-translate-y-1.5 transition-transform" />
                </button>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between px-6">
              <p className="text-[9px] text-white/20 font-black uppercase tracking-[0.3em] flex items-center gap-2">
                <CpuChipIcon className="w-3 h-3" />
                Asistente Industrial v1.0 Premium (Full Screen)
              </p>
              <div className="flex items-center gap-4">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50 animate-pulse" />
                <p className="text-[9px] text-white/20 font-black uppercase tracking-[0.3em]">IA Engine Active</p>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        {showPanel && (
          <DiagnosisPanel
            data={lastAnalysisData}
            onClose={() => setShowPanel(false)}
            onGenerateReport={generateReport}
            isGeneratingReport={isLoading}
          />
        )}
      </div>
    </div>
  );
}