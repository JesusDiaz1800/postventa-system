import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  SparklesIcon,
  PaperAirplaneIcon,
  PhotoIcon,
  XMarkIcon,
  ArrowPathIcon,
  LightBulbIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  WrenchScrewdriverIcon,
  TrashIcon,
  ChevronRightIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  BookOpenIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api, aiAgentsAPI } from '../services/api';
import { formatAnalysisResult } from '../utils/aiUtils';

// ============================================================================
// TYPES
// ============================================================================

interface AnalysisReport {
  severity_level: 'critical' | 'high' | 'medium' | 'low';
  observations: string;
  possible_causes: string[];
  recommendations: string[];
  corrective_actions: string[];
  preventive_measures: string[];
  required_tools: string[];
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    confidence?: number;
    reasoning?: string;
    sources?: string[];
    iterations?: number;
    hasImage?: boolean;
    imagePreview?: string;
    analysisData?: AnalysisReport;
  };
}

interface ThinkingStep {
  icon: React.ReactNode;
  text: string;
  done: boolean;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const CHAT_HISTORY_KEY = 'ai_chat_history_v2'; // Versioned key to avoid conflicts
const MAX_HISTORY = 50;

const SUGGESTION_PROMPTS = [
  '¿Cuáles son las causas de falla en soldaduras por polifusión?',
  '¿Cómo identificar un defecto de fabricación en tuberías PE?',
  '¿Qué normativas aplican para instalación de tuberías de presión?',
  'Analiza esta imagen de falla en accesorio',
];

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const DetailedReportPanel = ({ data, onClose }: { data: AnalysisReport, onClose: () => void }) => {
  const getSeverityColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 text-red-300 border-red-500/50';
      case 'high': return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
      case 'low': return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/50';
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[600px] bg-slate-900/95 backdrop-blur-xl border-l border-white/10 shadow-2xl p-6 overflow-y-auto transform transition-transform duration-300 ease-in-out z-50">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <ChartBarIcon className="w-7 h-7 text-purple-400" />
          Reporte Técnico Detallado
        </h2>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
          <XMarkIcon className="w-6 h-6 text-white/60" />
        </button>
      </div>

      <div className="space-y-8">
        {/* Severity Banner */}
        {data.severity_level && (
          <div className={`p-4 rounded-xl border flex items-center gap-4 ${getSeverityColor(data.severity_level)}`}>
            <ExclamationTriangleIcon className="w-8 h-8" />
            <div>
              <p className="text-xs uppercase tracking-wider font-bold opacity-80">Nivel de Gravedad</p>
              <p className="text-xl font-bold">{data.severity_level.toUpperCase()}</p>
            </div>
          </div>
        )}

        {/* Observations */}
        <section>
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <MagnifyingGlassIcon className="w-5 h-5 text-blue-400" />
            Observaciones
          </h3>
          <div className="bg-white/5 p-4 rounded-xl border border-white/5 text-white/80 leading-relaxed">
            {data.observations}
          </div>
        </section>

        {/* Causes & Recommendations Grid */}
        <div className="grid grid-cols-1 gap-6">
          <section>
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
              <ExclamationTriangleIcon className="w-5 h-5 text-rose-400" />
              Posibles Causas
            </h3>
            <ul className="space-y-2">
              {data.possible_causes?.map((cause, i) => (
                <li key={i} className="flex items-start gap-3 bg-red-500/5 p-3 rounded-lg border border-red-500/10">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-2 flex-shrink-0" />
                  <span className="text-white/80 text-sm">{cause.replace(/\*\*/g, '')}</span>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
              <LightBulbIcon className="w-5 h-5 text-amber-400" />
              Recomendaciones
            </h3>
            <ul className="space-y-2">
              {data.recommendations?.map((rec, i) => (
                <li key={i} className="flex items-start gap-3 bg-amber-500/5 p-3 rounded-lg border border-amber-500/10">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                  <span className="text-white/80 text-sm">{rec.replace(/\*\*/g, '')}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* Action Plan */}
        {(data.corrective_actions?.length > 0 || data.preventive_measures?.length > 0) && (
          <section className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 p-5 rounded-2xl border border-purple-500/20">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <ShieldCheckIcon className="w-5 h-5 text-purple-400" />
              Plan de Acción
            </h3>

            <div className="space-y-4">
              {data.corrective_actions?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-purple-200 mb-2 uppercase tracking-wide">Acciones Correctivas</h4>
                  <ul className="grid grid-cols-1 gap-2">
                    {data.corrective_actions.map((act, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-purple-100/80">
                        <CheckCircleIcon className="w-4 h-4 text-emerald-400" />
                        {act}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {data.preventive_measures?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-blue-200 mb-2 uppercase tracking-wide mt-4">Medidas Preventivas</h4>
                  <ul className="grid grid-cols-1 gap-2">
                    {data.preventive_measures.map((meas, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-blue-100/80">
                        <ShieldCheckIcon className="w-4 h-4 text-blue-400" />
                        {meas}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AIPage() {
  const { showSuccess, showError } = useNotifications();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState<ThinkingStep[]>([]);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<AnalysisReport | null>(null);

  // Load chat history
  useEffect(() => {
    try {
      const stored = localStorage.getItem(CHAT_HISTORY_KEY);
      if (stored) {
        setMessages(JSON.parse(stored));
      } else {
        setMessages([{
          id: 'welcome',
          role: 'assistant',
          content: '¡Hola! Soy tu asistente de IA Premium. Cuento con acceso a:\n\n• 📚 **Base de Conocimiento Arquitectónica**\n• 🛠️ **Normativas de Calidad y Postventa**\n• 👁️ **Análisis Visual Avanzado**\n\n¿En qué puedo asistirte hoy?',
          timestamp: new Date().toISOString(),
        }]);
      }
    } catch (e) {
      console.error('Error loading chat history:', e);
    }
  }, []);

  // Persist history
  useEffect(() => {
    if (messages.length > 0 && messages[0].id !== 'welcome') {
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages.slice(0, MAX_HISTORY)));
    }
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinkingSteps]);

  // AI Status
  const { data: aiStatus } = useQuery({
    queryKey: ['ai-status'],
    queryFn: async () => {
      try {
        const response = await api.get('/ai-agents/status/');
        return response.data;
      } catch {
        return { success: false, agent_ready: false };
      }
    },
    staleTime: 30000,
  });

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        showError('La imagen no debe superar los 10MB');
        return;
      }
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (ev) => setImagePreview(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSend = async () => {
    if ((!inputValue.trim() && !selectedImage) || isProcessing) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputValue.trim() || '(Imagen adjunta para análisis)',
      timestamp: new Date().toISOString(),
      metadata: selectedImage ? { hasImage: true, imagePreview: imagePreview || undefined } : undefined,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsProcessing(true);

    const steps = [
      { icon: <BookOpenIcon className="w-4 h-4" />, text: 'Consultando base de conocimiento...', done: false },
      { icon: <MagnifyingGlassIcon className="w-4 h-4" />, text: 'Analizando contexto...', done: false },
      { icon: <SparklesIcon className="w-4 h-4" />, text: 'Generando respuesta...', done: false },
    ];

    if (selectedImage) {
      steps.unshift({ icon: <PhotoIcon className="w-4 h-4" />, text: 'Procesando imagen...', done: false });
    }

    setThinkingSteps(steps);

    try {
      let response;

      if (selectedImage) {
        // Image Analysis
        const formData = new FormData();
        formData.append('image', selectedImage);
        formData.append('query', inputValue || 'Analiza esta imagen y detecta posibles fallas'); // Corrected param

        // Simulate step progression
        setThinkingSteps(prev => prev.map((s, i) => i === 0 ? { ...s, done: true } : s));

        const result = await api.post('/ai-agents/analyze-image/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        response = result.data;
      } else {
        // Text Query
        setThinkingSteps(prev => prev.map((s, i) => i === 0 ? { ...s, done: true } : s));

        const result = await aiAgentsAPI.query(inputValue);

        response = result.data;
      }

      setThinkingSteps(prev => prev.map(s => ({ ...s, done: true })));
      await new Promise(r => setTimeout(r, 400));

      const analysisData = response.analysisData || response.analysis_data; // Flexible key

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response || 'No se pudo generar respuesta',
        timestamp: new Date().toISOString(),
        metadata: {
          confidence: response.confidence,
          reasoning: response.reasoning,
          sources: response.sources,
          iterations: response.iterations,
          analysisData: typeof analysisData === 'string' ? JSON.parse(analysisData) : analysisData,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);
      clearImage();

    } catch (error: any) {
      console.error('AI Error:', error);
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠️ Lo siento, hubo un error al procesar tu solicitud. ${error.response?.data?.error || ''}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
      setThinkingSteps([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 relative overflow-hidden">

      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-20 -left-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Main Chat Area */}
      <div className={`flex flex-col flex-1 transition-all duration-300 ${selectedReport ? 'mr-0 md:mr-[600px]' : ''}`}>

        {/* Header */}
        <div className="flex-shrink-0 px-6 py-4 border-b border-white/5 bg-black/20 backdrop-blur-md z-10 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-purple-500/20">
              <SparklesIcon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">AI Assistant <span className="text-purple-400 font-normal ml-1">Premium</span></h1>
              <p className="text-xs text-white/40 flex items-center gap-2">
                {aiStatus?.agent_ready ? (
                  <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Online</span>
                ) : (
                  <span className="text-amber-400">Connecting...</span>
                )}
                <span className="opacity-50">•</span>
                <span>RAG Enabled</span>
              </p>
            </div>
          </div>
          <button onClick={() => { localStorage.removeItem(CHAT_HISTORY_KEY); setMessages([]); }} className="text-white/30 hover:text-white/80 transition-colors">
            <TrashIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
              <div className={`max-w-[85%] md:max-w-2xl rounded-2xl p-4 shadow-xl backdrop-blur-sm border ${msg.role === 'user'
                  ? 'bg-gradient-to-br from-purple-600 to-indigo-600 border-white/10 text-white'
                  : 'bg-white/5 border-white/5 text-white/90'
                }`}>

                {/* User Image */}
                {msg.metadata?.imagePreview && (
                  <div className="mb-3 rounded-lg overflow-hidden border border-white/20">
                    <img src={msg.metadata.imagePreview} alt="Context" className="w-full max-h-60 object-cover" />
                  </div>
                )}

                {/* Content */}
                <div className="prose prose-invert prose-sm max-w-none leading-relaxed">
                  {msg.content.split('\n').map((line, i) => (
                    <p key={i} className={`min-h-[1.5em] ${line.startsWith('•') || line.startsWith('-') ? 'ml-4' : ''}`}>
                      {line.replace(/\*\*(.*?)\*\*/g, (_, text) => `<strong>${text}</strong>`)}
                    </p>
                  ))}
                </div>

                {/* Analysis Report Card (Interactive) */}
                {msg.metadata?.analysisData && (
                  <div
                    onClick={() => setSelectedReport(msg.metadata!.analysisData!)}
                    className="mt-4 group cursor-pointer relative overflow-hidden rounded-xl border border-purple-500/30 bg-purple-500/10 p-4 transition-all hover:bg-purple-500/20 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-purple-500/20 text-purple-300 group-hover:bg-purple-500/30 group-hover:text-white transition-colors">
                          <ChartBarIcon className="w-6 h-6" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-white group-hover:text-purple-200 transition-colors">Ver Reporte Detallado</h3>
                          <p className="text-xs text-white/50">Clic para explorar causas y soluciones</p>
                        </div>
                      </div>
                      <ChevronRightIcon className="w-5 h-5 text-white/30 group-hover:text-white group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                )}

                {/* Footer / Metadata */}
                {msg.role === 'assistant' && (
                  <div className="mt-3 pt-3 border-t border-white/5 flex flex-wrap items-center gap-3 text-[10px] text-white/40">
                    {msg.metadata?.confidence && (
                      <span className={`px-2 py-0.5 rounded-full border ${msg.metadata.confidence > 0.8 ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                        }`}>
                        {Math.round(msg.metadata.confidence * 100)}% fiabilidad
                      </span>
                    )}
                    {msg.metadata?.sources?.length ? (
                      <span className="flex items-center gap-1">
                        <BookOpenIcon className="w-3 h-3" />
                        {msg.metadata.sources.length} fuentes
                      </span>
                    ) : null}
                    <span className="ml-auto opacity-50">
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Thinking State */}
          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-white/5 backdrop-blur rounded-2xl p-4 border border-white/5 max-w-sm w-full">
                <div className="space-y-3">
                  {thinkingSteps.map((step, i) => (
                    <div key={i} className={`flex items-center gap-3 text-sm transition-all duration-300 ${step.done ? 'text-emerald-400 opacity-50' : i === thinkingSteps.findIndex(s => !s.done) ? 'text-white' : 'text-white/20'}`}>
                      {step.done ? <CheckCircleIcon className="w-5 h-5" /> : (i === thinkingSteps.findIndex(s => !s.done) ? <ArrowPathIcon className="w-5 h-5 animate-spin text-purple-400" /> : step.icon)}
                      <span className="font-medium">{step.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0 p-6 bg-black/20 backdrop-blur-xl border-t border-white/5">
          <div className="max-w-4xl mx-auto relative">

            {/* Image Preview Overlay */}
            {imagePreview && (
              <div className="absolute bottom-full left-0 mb-4 p-2 bg-slate-800 rounded-xl border border-white/10 shadow-2xl animate-in slide-in-from-bottom-2">
                <div className="relative">
                  <img src={imagePreview} alt="Upload" className="h-32 rounded-lg" />
                  <button onClick={clearImage} className="absolute -top-2 -right-2 p-1 bg-red-500 rounded-full text-white hover:bg-red-600 shadow-lg">
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            <div className="flex gap-4 items-end">
              <button
                onClick={() => fileInputRef.current?.click()}
                className={`p-4 rounded-2xl transition-all border ${selectedImage ? 'bg-purple-500/20 border-purple-500/50 text-purple-300' : 'bg-white/5 border-white/5 text-white/60 hover:bg-white/10 hover:text-white'}`}
              >
                <PhotoIcon className="w-6 h-6" />
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />

              <div className="flex-1 bg-white/5 rounded-2xl border border-white/5 focus-within:border-purple-500/50 focus-within:bg-white/10 transition-all flex items-end">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Describe tu problema o sube una imagen..."
                  className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-white/30 py-4 px-4 min-h-[60px] max-h-32 resize-none"
                  style={{ minHeight: '60px' }}
                />
                <button
                  onClick={handleSend}
                  disabled={(!inputValue.trim() && !selectedImage) || isProcessing}
                  className="m-2 p-3 rounded-xl bg-purple-600 text-white shadow-lg shadow-purple-500/20 hover:bg-purple-500 hover:shadow-purple-500/40 disabled:opacity-50 disabled:shadow-none transition-all"
                >
                  {isProcessing ? <ArrowPathIcon className="w-5 h-5 animate-spin" /> : <PaperAirplaneIcon className="w-5 h-5 -rotate-45 translate-x-0.5 -translate-y-0.5" />}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Side Panel (Detailed Report) */}
      {selectedReport && (
        <DetailedReportPanel data={selectedReport} onClose={() => setSelectedReport(null)} />
      )}

      {/* Overlay for mobile when panel is open */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm" onClick={() => setSelectedReport(null)} />
      )}
    </div>
  );
}

export default AIPage;