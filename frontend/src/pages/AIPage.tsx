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
  ClipboardDocumentIcon,
  CloudIcon,
  WifiIcon,
} from '@heroicons/react/24/outline';
import { useAIChat, ChatMessage, EngineProvider } from '../hooks/useAIChat';

// ============================================================================
// Helpers
// ============================================================================
function formatBold(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
    .replace(/`([^`]+)`/g, '<code class="bg-black/40 px-1.5 py-0.5 rounded text-amber-300 font-mono text-xs border border-white/5 whitespace-nowrap">$1</code>');
}

function renderMarkdown(text: string) {
  return text.split('\n').map((line, i) => {
    if (line.startsWith('### '))
      return <h3 key={i} className="text-base font-black text-indigo-200 mt-5 mb-2 flex items-center gap-2 before:content-['▸'] before:text-indigo-500">{line.replace('### ', '')}</h3>;
    if (line.startsWith('## '))
      return <h2 key={i} className="text-lg font-black text-white mt-6 mb-3 border-b border-white/5 pb-2">{line.replace('## ', '')}</h2>;
    if (line.trim().startsWith('- ') || line.trim().startsWith('• '))
      return (
        <div key={i} className="flex gap-2.5 ml-4 mb-1.5 items-start">
          <span className="text-indigo-400 mt-1 shrink-0">▸</span>
          <span className="text-slate-300 leading-relaxed" dangerouslySetInnerHTML={{ __html: formatBold(line.replace(/^[-•]\s+/, '')) }} />
        </div>
      );
    if (/^\d+\.\s/.test(line))
      return (
        <div key={i} className="flex gap-2.5 ml-4 mb-1.5 items-start">
          <span className="text-indigo-400 font-mono text-xs mt-1 shrink-0 font-black">{line.match(/^\d+\./)?.[0]}</span>
          <span className="text-slate-300 leading-relaxed" dangerouslySetInnerHTML={{ __html: formatBold(line.replace(/^\d+\.\s+/, '')) }} />
        </div>
      );
    if (!line.trim()) return <div key={i} className="h-2" />;
    return (
      <p key={i} className="mb-2.5 leading-relaxed text-slate-300/90"
        dangerouslySetInnerHTML={{ __html: formatBold(line) }} />
    );
  });
}

// ============================================================================
// Engine Badge
// ============================================================================
function EngineBadge({ provider }: { provider: EngineProvider }) {
  const isLocal = provider === 'ollama-local' || provider === 'local-heuristics' || provider === 'local';
  const isCloud = provider === 'google' || provider === 'openai' || provider === 'anthropic';

  if (!isLocal && !isCloud) return null;

  return (
    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[8px] font-black uppercase tracking-widest border ${
      isCloud
        ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300'
        : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
    }`}>
      {isCloud ? <CloudIcon className="w-3 h-3" /> : <CpuChipIcon className="w-3 h-3" />}
      {isCloud ? 'Gemini Cloud' : provider === 'ollama-local' ? 'Ollama Local' : 'Motor Local'}
    </div>
  );
}

// ============================================================================
// COMPONENT: Chat Message Bubble
// ============================================================================
const MessageBubble = ({ message, onOpenReport, onCopy }: {
  message: ChatMessage;
  onOpenReport: (data: any) => void;
  onCopy: (text: string) => void;
}) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 group animate-fadeIn`}>
      {!isUser && (
        <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-xl shadow-indigo-900/30 mr-3 shrink-0 mt-1">
          <SparklesIcon className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={`relative max-w-[88%] rounded-[1.5rem] p-5 shadow-xl border transition-all duration-300 ${
        isUser
          ? 'bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 border-white/10 text-white rounded-br-sm'
          : 'bg-[#141921] border-white/5 text-slate-200 rounded-bl-sm hover:border-indigo-500/10'
        }`}>

        {/* Subtle glow for AI messages */}
        {!isUser && (
          <div className="absolute -inset-px bg-gradient-to-br from-indigo-500/5 to-transparent rounded-[1.5rem] -z-10 group-hover:from-indigo-500/10 transition-all" />
        )}

        {/* Image Previews */}
        {message.metadata?.imagePreviews && message.metadata.imagePreviews.length > 0 && (
          <div className="grid grid-cols-2 gap-2.5 mb-4">
            {message.metadata.imagePreviews.map((preview, idx) => (
              <div key={idx} className="relative aspect-[16/10] rounded-xl overflow-hidden border border-white/10 group/img">
                <img src={preview} alt={`Adjunto ${idx + 1}`} className="w-full h-full object-cover transition-transform duration-700 group-hover/img:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
              </div>
            ))}
          </div>
        )}

        {/* Markdown Content */}
        <div className="prose prose-invert prose-sm max-w-none text-[0.85rem] leading-relaxed">
          {renderMarkdown(message.content)}
        </div>

        {/* Assistant Footer */}
        {!isUser && (
          <div className="mt-5 pt-4 border-t border-white/5 flex flex-wrap gap-2 items-center">
            {/* Confidence */}
            {message.metadata?.confidence !== undefined && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/30 border border-white/5 text-[8px] font-black uppercase tracking-wider text-emerald-400">
                <ShieldCheckIcon className="w-3 h-3" />
                {Math.round(message.metadata.confidence * 100)}% fiabilidad
              </div>
            )}

            {/* Engine */}
            {message.metadata?.engineProvider && (
              <EngineBadge provider={message.metadata.engineProvider} />
            )}

            {/* Sources */}
            {message.metadata?.sources && message.metadata.sources.length > 0 && (
              message.metadata.sources.map((source, idx) => (
                <div key={idx} className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[8px] font-bold uppercase tracking-wider">
                  <DocumentTextIcon className="w-3 h-3" />
                  {source.replace(' (NotebookLM)', '')}
                </div>
              ))
            )}

            <div className="flex-1" />

            {/* Copy */}
            <button
              onClick={handleCopy}
              className="p-1.5 hover:bg-white/5 rounded-lg text-white/30 hover:text-white transition-all"
              title="Copiar respuesta"
            >
              {copied
                ? <CheckCircleIcon className="w-4 h-4 text-emerald-400" />
                : <ClipboardDocumentIcon className="w-4 h-4" />
              }
            </button>

            {/* View Diagnosis */}
            {message.metadata?.analysisData && (
              <button
                onClick={() => onOpenReport(message.metadata?.analysisData)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 hover:bg-indigo-500 hover:text-white transition-all text-[8px] font-black uppercase tracking-widest"
              >
                <ChartBarIcon className="w-3.5 h-3.5" />
                Ver Diagnóstico
              </button>
            )}

            {/* Open Report */}
            {message.metadata?.reportHtml && (
              <button
                onClick={() => {
                  const win = window.open('', '_blank');
                  win?.document.write(message.metadata!.reportHtml!);
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 hover:bg-blue-500 hover:text-white transition-all text-[8px] font-black uppercase tracking-widest"
              >
                <DocumentTextIcon className="w-3.5 h-3.5" />
                Abrir Reporte
              </button>
            )}
          </div>
        )}

        {/* User timestamp */}
        {isUser && (
          <p className="text-[9px] text-white/30 mt-3 text-right font-mono">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// COMPONENT: Loading Indicator — context-aware
// ============================================================================
const LoadingIndicator = ({ provider }: { provider: 'Gemini' | 'Ollama' }) => (
  <div className="flex justify-start mb-6 animate-fadeIn">
    <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600/50 to-purple-600/50 flex items-center justify-center mr-3 shrink-0 mt-1 animate-pulse">
      <SparklesIcon className="w-4 h-4 text-white/50" />
    </div>
    <div className="bg-[#141921] border border-white/5 px-5 py-4 rounded-[1.5rem] rounded-bl-sm flex items-center gap-4 shadow-xl max-w-[280px]">
      <div className="flex gap-1.5">
        <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <div>
        <p className="text-[9px] font-black uppercase tracking-widest text-indigo-300">
          {provider === 'Ollama' ? 'Motor Local Procesando' : 'Analizando con Gemini'}
        </p>
        {provider === 'Ollama' && (
          <p className="text-[8px] text-white/20 mt-0.5 font-medium">Puede tardar ~30–90s</p>
        )}
      </div>
    </div>
  </div>
);

// ============================================================================
// COMPONENT: Diagnosis Panel
// ============================================================================
const DiagnosisPanel = ({ data, onClose, onGenerateReport, isGeneratingReport }: {
  data: any;
  onClose: () => void;
  onGenerateReport: () => void;
  isGeneratingReport: boolean;
}) => {
  if (!data) return null;

  const severityColor: Record<string, string> = {
    'Baja': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    'Media': 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    'Alta': 'text-orange-400 bg-orange-500/10 border-orange-500/20',
    'Crítica': 'text-red-400 bg-red-500/10 border-red-500/20',
    'Informativa': 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  };
  const severityClass = severityColor[data.severity_level] || 'text-white/50 bg-white/5 border-white/10';

  return (
    <div className="absolute inset-y-0 right-0 w-full md:w-[580px] bg-[#05080F]/95 backdrop-blur-3xl border-l border-white/10 shadow-[0_0_60px_rgba(0,0,0,0.6)] p-8 overflow-y-auto z-30 animate-slideInRight custom-scrollbar">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">
            Análisis <span className="text-indigo-500">Técnico</span>
          </h2>
          <p className="text-white/30 text-[10px] font-black uppercase tracking-[0.2em] mt-1">Sistema de Asistencia Industrial</p>
        </div>
        <div className="flex items-center gap-3">
          {data.severity_level && (
            <div className={`px-3 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest border ${severityClass}`}>
              {data.severity_level}
            </div>
          )}
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-xl transition-colors text-white/40 hover:text-white border border-transparent hover:border-white/10">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="space-y-5">
        {/* Observations */}
        <div className="bg-[#0D1117] rounded-2xl p-5 border border-white/5">
          <h3 className="text-[9px] font-black text-indigo-400 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
            <MagnifyingGlassIcon className="w-3.5 h-3.5" /> Hallazgos Visuales
          </h3>
          <p className="text-slate-300 text-sm leading-relaxed">{data.observations || "Sin datos disponibles."}</p>
        </div>

        {/* Failure Type & Material */}
        {(data.failure_type || data.material_identification) && (
          <div className="grid grid-cols-2 gap-3">
            {data.failure_type && (
              <div className="bg-[#0D1117] rounded-2xl p-4 border border-white/5">
                <h3 className="text-[9px] font-black text-white/30 uppercase tracking-[0.2em] mb-2">Tipo de Falla</h3>
                <p className="text-white text-sm font-bold">{data.failure_type}</p>
              </div>
            )}
            {data.material_identification && (
              <div className="bg-[#0D1117] rounded-2xl p-4 border border-white/5">
                <h3 className="text-[9px] font-black text-white/30 uppercase tracking-[0.2em] mb-2">Material</h3>
                <p className="text-white text-sm font-bold">{data.material_identification}</p>
              </div>
            )}
          </div>
        )}

        {/* Causes */}
        {data.possible_causes && data.possible_causes.length > 0 && (
          <div className="bg-[#0D1117] rounded-2xl p-5 border border-red-500/10">
            <h3 className="text-[9px] font-black text-rose-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <ExclamationTriangleIcon className="w-3.5 h-3.5" /> Causas Probables
            </h3>
            <div className="space-y-2.5">
              {data.possible_causes.map((cause: string, i: number) => (
                <div key={i} className="flex gap-3 items-start bg-rose-500/5 px-4 py-3 rounded-xl border border-rose-500/10">
                  <div className="w-5 h-5 rounded-lg bg-rose-500/20 flex items-center justify-center text-rose-400 text-[10px] font-black shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <p className="text-slate-300 text-sm">{cause}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {data.recommendations && data.recommendations.length > 0 && (
          <div className="bg-[#0D1117] rounded-2xl p-5 border border-emerald-500/10">
            <h3 className="text-[9px] font-black text-emerald-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <LightBulbIcon className="w-3.5 h-3.5" /> Recomendaciones
            </h3>
            <div className="space-y-2.5">
              {data.recommendations.map((rec: string, i: number) => (
                <div key={i} className="flex gap-3 items-start bg-emerald-500/5 px-4 py-3 rounded-xl border border-emerald-500/10">
                  <CheckCircleIcon className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <p className="text-slate-300 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Corrective Actions */}
        {data.corrective_actions && data.corrective_actions.length > 0 && (
          <div className="bg-[#0D1117] rounded-2xl p-5 border border-amber-500/10">
            <h3 className="text-[9px] font-black text-amber-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <ArrowPathIcon className="w-3.5 h-3.5" /> Acciones Correctivas
            </h3>
            <div className="space-y-2.5">
              {data.corrective_actions.map((action: string, i: number) => (
                <div key={i} className="flex gap-3 items-start bg-amber-500/5 px-4 py-3 rounded-xl border border-amber-500/10">
                  <span className="text-amber-400 font-black text-xs shrink-0 mt-0.5">→</span>
                  <p className="text-slate-300 text-sm">{action}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Technical Notes */}
        {data.technical_notes && (
          <div className="bg-[#0D1117] rounded-2xl p-5 border border-white/5">
            <h3 className="text-[9px] font-black text-blue-400 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
              <DocumentTextIcon className="w-3.5 h-3.5" /> Notas Técnicas
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed italic">{data.technical_notes}</p>
          </div>
        )}

        {/* Generate Report CTA */}
        <div className="pt-4">
          <button
            onClick={onGenerateReport}
            disabled={isGeneratingReport}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-black uppercase tracking-[0.15em] shadow-2xl shadow-indigo-500/25 disabled:opacity-50 flex items-center justify-center gap-3 transition-all active:scale-[0.98]"
          >
            {isGeneratingReport
              ? <><ArrowPathIcon className="w-5 h-5 animate-spin" /> Generando Reporte...</>
              : <><DocumentTextIcon className="w-5 h-5" /> Generar Informe Oficial</>
            }
          </button>
          <p className="text-[9px] text-white/20 font-bold uppercase tracking-widest text-center mt-3 flex items-center justify-center gap-1.5">
            <ShieldCheckIcon className="w-3 h-3" />
            Sistema Inteligente de Postventa
          </p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// QUICK PROMPTS
// ============================================================================
const QUICK_PROMPTS = [
  '¿Cuáles son los pasos para soldadura por polifusión?',
  '¿Cómo identificar una falla de instalación en tubería HDPE?',
  '¿Cuáles son las normativas ISO para accesorios de polietileno?',
  '¿Cuántas incidencias hay abiertas este mes?',
];

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
    setProvider,
    lastEngineProvider,
  } = useAIChat();

  const [inputValue, setInputValue] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [filePreviews, setFilePreviews] = useState<string[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px';
    }
  }, [inputValue]);

  // Show panel when analysis arrives
  useEffect(() => {
    if (lastAnalysisData) setShowPanel(true);
  }, [lastAnalysisData]);

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

  const handleSend = async () => {
    if (!inputValue.trim() && selectedFiles.length === 0) return;
    await sendMessage(inputValue, selectedFiles);
    setInputValue('');
    setSelectedFiles([]);
    setFilePreviews([]);
  };

  // Drag & Drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    if (files.length) {
      const combined = [...selectedFiles, ...files].slice(0, 5);
      setSelectedFiles(combined);
      Promise.all(combined.map(f => new Promise<string>(r => {
        const reader = new FileReader();
        reader.onload = (ev) => r(ev.target!.result as string);
        reader.readAsDataURL(f);
      }))).then(setFilePreviews);
    }
  };

  // Engine status indicator
  const isLocalEngine = lastEngineProvider === 'ollama-local' || lastEngineProvider === 'local-heuristics' || lastEngineProvider === 'local';
  const isCloudEngine = lastEngineProvider === 'google' || lastEngineProvider === 'openai';

  return (
    <div
      className="flex h-[calc(100vh-4rem)] bg-[#0B0F19] text-white overflow-hidden font-sans selection:bg-indigo-500/30"
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      {/* Drag Overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 bg-indigo-600/20 backdrop-blur-sm border-4 border-dashed border-indigo-500/50 flex items-center justify-center pointer-events-none animate-fadeIn">
          <div className="text-center">
            <PhotoIcon className="w-16 h-16 text-indigo-400 mx-auto mb-4 animate-bounce" />
            <p className="text-2xl font-black text-white uppercase tracking-tighter">Suelta para Analizar</p>
            <p className="text-white/40 text-sm mt-2">Hasta 5 imágenes</p>
          </div>
        </div>
      )}

      {/* ================================================================
          SIDEBAR
      ================================================================ */}
      <div className="w-[72px] md:w-60 bg-[#05080F] border-r border-white/[0.04] flex flex-col items-center md:items-stretch py-6 md:px-4 z-10 shrink-0">

        {/* Logo */}
        <div className="mb-6 flex flex-col items-center md:flex-row md:items-center md:gap-3 md:px-1">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-xl shadow-indigo-900/40 shrink-0">
            <SparklesIcon className="w-6 h-6 text-white" />
          </div>
          <div className="hidden md:block">
            <h1 className="font-black text-base leading-none tracking-tight uppercase">Asistente <span className="text-indigo-500">IA</span></h1>
            <p className="text-[9px] text-white/25 font-bold uppercase tracking-[0.15em] mt-0.5">Industrial Premium</p>
          </div>
        </div>

        {/* Engine Status */}
        {(isLocalEngine || isCloudEngine) && (
          <div className={`hidden md:flex items-center gap-2 px-3 py-2 rounded-xl border mb-4 text-[9px] font-black uppercase tracking-wider ${
            isCloudEngine
              ? 'bg-indigo-500/5 border-indigo-500/15 text-indigo-400'
              : 'bg-emerald-500/5 border-emerald-500/15 text-emerald-400'
          }`}>
            {isCloudEngine ? <CloudIcon className="w-3.5 h-3.5" /> : <CpuChipIcon className="w-3.5 h-3.5" />}
            {isCloudEngine ? 'Gemini Cloud' : 'Motor Local'}
          </div>
        )}

        {/* Provider Toggle */}
        <div className="mb-5 p-1 bg-black/50 backdrop-blur-md rounded-2xl border border-white/[0.04] flex gap-1">
          <button
            onClick={() => setProvider('Gemini')}
            className={`flex-1 py-3 px-2 rounded-xl flex items-center justify-center gap-1.5 transition-all duration-200 ${
              provider === 'Gemini'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/40'
                : 'text-white/30 hover:text-white/60'
            }`}
            title="Gemini (Nube)"
          >
            <CloudIcon className={`w-4 h-4 ${provider === 'Gemini' ? '' : ''}`} />
            <span className="text-[9px] font-black uppercase tracking-widest hidden md:inline">Nube</span>
          </button>
          <button
            onClick={() => setProvider('Ollama')}
            className={`flex-1 py-3 px-2 rounded-xl flex items-center justify-center gap-1.5 transition-all duration-200 ${
              provider === 'Ollama'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40'
                : 'text-white/30 hover:text-white/60'
            }`}
            title="Ollama (Local)"
          >
            <CpuChipIcon className="w-4 h-4" />
            <span className="text-[9px] font-black uppercase tracking-widest hidden md:inline">Local</span>
          </button>
        </div>

        {/* New Chat */}
        <button
          onClick={clearChat}
          className="w-full bg-white/[0.03] hover:bg-white/[0.06] text-white/50 hover:text-white p-3 md:px-4 md:py-3 rounded-xl flex items-center justify-center md:justify-start gap-2.5 transition-all border border-white/[0.04] group mb-5"
        >
          <ArrowPathIcon className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500 shrink-0" />
          <span className="hidden md:inline text-[10px] font-bold uppercase tracking-widest">Nueva Consulta</span>
        </button>

        {/* Session label */}
        <div className="hidden md:block px-2">
          <p className="text-[8px] font-black uppercase tracking-[0.25em] text-white/15 mb-2">Sesión Actual</p>
          <div className="px-3 py-2.5 rounded-xl bg-indigo-500/8 border border-indigo-500/15 text-[9px] font-bold uppercase tracking-widest text-indigo-400">
            Diagnóstico Activo
          </div>
        </div>

        <div className="flex-1" />

        {/* Footer hint */}
        <div className="hidden md:block p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] text-[8px] leading-relaxed text-white/20 font-medium">
          Analiza fallas, consulta normativas y obtén diagnósticos técnicos en tiempo real.
        </div>
      </div>

      {/* ================================================================
          MAIN CHAT
      ================================================================ */}
      <div className="flex-1 flex flex-col relative min-w-0 bg-[radial-gradient(ellipse_at_50%_0%,rgba(79,70,229,0.04)_0%,transparent_60%)]">

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 md:py-8 custom-scrollbar scroll-smooth">
          <div className="max-w-3xl mx-auto">

            {/* Empty State */}
            {messages.length === 0 && (
              <div className="h-[55vh] flex flex-col items-center justify-center text-center animate-fadeIn">
                <div className="relative w-20 h-20 mb-8">
                  <div className="w-20 h-20 rounded-[1.8rem] bg-indigo-600/10 border border-indigo-600/20 flex items-center justify-center">
                    <SparklesIcon className="w-10 h-10 text-indigo-400" />
                  </div>
                  <div className="absolute -inset-4 bg-indigo-500/5 rounded-full blur-3xl animate-pulse" />
                </div>
                <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-3">
                  ¿En qué puedo <span className="text-indigo-500">ayudarte</span>?
                </h2>
                <p className="text-white/30 max-w-sm text-sm font-medium mb-10">
                  Diagnóstico técnico de imágenes, consultas de normativas industriales y análisis de incidencias.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-xl">
                  {QUICK_PROMPTS.map((hint, i) => (
                    <button
                      key={i}
                      onClick={() => setInputValue(hint)}
                      className="px-4 py-3 rounded-2xl bg-white/[0.03] border border-white/8 text-xs font-medium text-white/50 hover:border-indigo-500/30 hover:bg-indigo-500/5 hover:text-white/80 transition-all text-left leading-snug"
                    >
                      {hint}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                onOpenReport={(data) => { setLastAnalysisData(data); setShowPanel(true); }}
                onCopy={(text) => navigator.clipboard.writeText(text)}
              />
            ))}

            {/* Loading */}
            {isLoading && <LoadingIndicator provider={provider} />}

            {/* Error */}
            {error && (
              <div className="flex justify-center mb-6 animate-fadeIn">
                <div className="bg-red-500/8 border border-red-500/20 text-red-300 px-5 py-3.5 rounded-2xl text-xs font-bold uppercase tracking-widest flex items-center gap-3 shadow-xl shadow-red-500/5 max-w-lg">
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-400 shrink-0" />
                  {error}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} className="h-4" />
          </div>
        </div>

        {/* ============================================================
            INPUT AREA
        ============================================================ */}
        <div className="px-4 pb-5 md:px-8 md:pb-7 z-20 shrink-0">
          <div className="max-w-3xl mx-auto">

            {/* File Previews */}
            {filePreviews.length > 0 && (
              <div className="flex gap-3 mb-4 overflow-x-auto pb-1">
                {filePreviews.map((src, i) => (
                  <div key={i} className="relative w-20 h-20 rounded-xl overflow-hidden border-2 border-indigo-500/40 group shrink-0 animate-scaleIn shadow-xl">
                    <img src={src} alt="Upload" className="w-full h-full object-cover" />
                    <button
                      onClick={() => removeFile(i)}
                      className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"
                    >
                      <TrashIcon className="w-5 h-5 text-red-400" />
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-20 h-20 border-2 border-dashed border-white/10 rounded-xl flex flex-col items-center justify-center text-white/20 hover:border-indigo-500/40 hover:text-indigo-400 transition-all shrink-0 bg-white/[0.02]"
                >
                  <PhotoIcon className="w-5 h-5 mb-1" />
                  <span className="text-[8px] font-black uppercase">Añadir</span>
                </button>
              </div>
            )}

            {/* Input Box */}
            <div className={`relative flex gap-3 items-end bg-[#141921] p-3 rounded-[2rem] border transition-all duration-300 shadow-2xl ${
              isDragging
                ? 'border-indigo-500/60 shadow-indigo-500/10'
                : 'border-white/[0.06] focus-within:border-indigo-500/40 focus-within:shadow-indigo-500/5'
            }`}>

              {/* Attach */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`p-4 rounded-[1.5rem] transition-all border shrink-0 ${
                  selectedFiles.length > 0
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-900/40'
                    : 'bg-white/[0.04] border-white/[0.04] text-white/40 hover:bg-white/8 hover:text-white'
                }`}
              >
                <PhotoIcon className="w-6 h-6" />
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" multiple className="hidden" onChange={handleFileSelect} />

              {/* Textarea */}
              <div className="flex-1 min-h-[52px] flex items-center">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                  placeholder="Consulta sobre incidencias, normativas o sube imágenes para analizar..."
                  className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-white/20 py-3.5 px-2 resize-none font-medium text-[0.9rem] leading-snug overflow-hidden"
                  rows={1}
                  style={{ maxHeight: '160px' }}
                />
              </div>

              {/* Send */}
              <button
                onClick={handleSend}
                disabled={isLoading || (!inputValue.trim() && selectedFiles.length === 0)}
                className="p-4 rounded-[1.5rem] bg-indigo-600 text-white shadow-xl shadow-indigo-900/30 hover:bg-indigo-500 disabled:opacity-20 disabled:cursor-not-allowed transition-all active:scale-95 shrink-0"
              >
                <PaperAirplaneIcon className="w-5 h-5 -rotate-45" />
              </button>
            </div>

            {/* Footer meta */}
            <div className="mt-3 flex items-center justify-between px-4">
              <p className="text-[8px] text-white/15 font-bold uppercase tracking-[0.3em] flex items-center gap-1.5">
                <WifiIcon className="w-3 h-3" />
                Asistente IA Industrial v2.0
              </p>
              <p className="text-[8px] text-white/15 font-medium">Enter para enviar · Shift+Enter = nueva línea</p>
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