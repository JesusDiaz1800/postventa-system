import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
    XMarkIcon,
    PaperAirplaneIcon,
    MinusIcon,
    SparklesIcon,
    ArrowPathIcon,
    PhotoIcon,
    ChatBubbleOvalLeftEllipsisIcon,
    ArrowsPointingOutIcon,
    CpuChipIcon,
    TrashIcon
} from '@heroicons/react/24/outline';
import { useAIChat } from '../hooks/useAIChat';

export function FloatingAIChat() {
    const location = useLocation();
    const navigate = useNavigate();

    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);
    const [inputValue, setInputValue] = useState('');
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [filePreviews, setFilePreviews] = useState<string[]>([]);

    // Use Shared Hook
    const { messages, isLoading, sendMessage, refreshHistory, provider, setProvider } = useAIChat();

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Refresh history when opening
    useEffect(() => {
        if (isOpen && !isMinimized) {
            refreshHistory();
            setUnreadCount(0);
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [isOpen, isMinimized, refreshHistory]);

    // Simple scroll to bottom
    useEffect(() => {
        if (isOpen && !isMinimized) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isOpen, isMinimized]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            const combined = [...selectedFiles, ...newFiles].slice(0, 5);
            setSelectedFiles(combined);

            Promise.all(newFiles.map(f => new Promise<string>(r => {
                const reader = new FileReader();
                reader.onload = (ev) => r(ev.target!.result as string);
                reader.readAsDataURL(f);
            }))).then(previews => setFilePreviews(previews));
        }
    };

    const clearFiles = () => {
        setSelectedFiles([]);
        setFilePreviews([]);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const handleSend = async () => {
        if ((!inputValue.trim() && selectedFiles.length === 0) || isLoading) return;

        await sendMessage(inputValue, selectedFiles);
        setInputValue('');
        clearFiles();
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Hide on AI Page
    if (location.pathname === '/ai') return null;

    if (!isOpen) {
        return (
            <button
                onClick={() => { setIsOpen(true); setIsMinimized(false); }}
                className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-[1.5rem] shadow-[0_10px_30px_rgba(79,70,229,0.4)] flex items-center justify-center text-white hover:scale-110 transition-all duration-300 z-50 group animate-fadeIn"
            >
                <div className="relative">
                    <ChatBubbleOvalLeftEllipsisIcon className="w-9 h-9" />
                    <div className="absolute -inset-2 bg-white/20 rounded-full blur opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-lg text-xs flex items-center justify-center font-black border-2 border-[#0B0F19]">
                        {unreadCount}
                    </span>
                )}
            </button>
        );
    }

    if (isMinimized) {
        return (
            <div className="fixed bottom-6 right-6 w-72 bg-[#0B0F19]/90 border border-white/10 rounded-2xl z-50 overflow-hidden shadow-2xl backdrop-blur-xl animate-scaleIn">
                <div className="p-4 bg-white/5 flex items-center justify-between">
                    <span className="text-white text-xs font-black uppercase tracking-widest flex items-center gap-2">
                        <SparklesIcon className="w-4 h-4 text-indigo-400" /> Asistente IA
                    </span>
                    <div className="flex items-center gap-2">
                        <button onClick={() => setIsMinimized(false)} className="text-white/40 hover:text-white transition-colors p-1.5 bg-white/5 rounded-lg">
                            <ArrowsPointingOutIcon className="w-4 h-4" />
                        </button>
                        <button onClick={() => setIsOpen(false)} className="text-white/40 hover:text-white transition-colors p-1.5 bg-white/5 rounded-lg">
                            <XMarkIcon className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 w-[400px] h-[650px] max-h-[85vh] bg-[#0B0F19]/95 border border-white/10 z-50 flex flex-col rounded-[2.5rem] overflow-hidden shadow-[0_20px_60px_rgba(0,0,0,0.6)] animate-slideInRight backdrop-blur-3xl font-sans">
            {/* Header */}
            <div className="px-6 py-5 bg-white/5 flex items-center justify-between flex-shrink-0 border-b border-white/5">
                <div className="flex items-center gap-4">
                    <div className="w-11 h-11 rounded-[1.2rem] bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <SparklesIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h3 className="text-white font-black text-sm tracking-tighter uppercase">Asistente <span className="text-indigo-500">IA</span></h3>
                        <div className="flex items-center gap-2 mt-0.5">
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_5px_rgba(16,185,129,0.5)]"></span>
                            <p className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] -mt-0.5">Asistente Virtual</p>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {/* Mini Provider Toggle */}
                    <div className="flex bg-black/40 rounded-lg p-0.5 border border-white/5 mr-2">
                        <button 
                            onClick={() => setProvider('Gemini')}
                            className={`p-1 rounded-md transition-all ${provider === 'Gemini' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-white/20'}`}
                            title="Usar Gemini (Nube)"
                        >
                            <SparklesIcon className="w-3.5 h-3.5" />
                        </button>
                        <button 
                            onClick={() => setProvider('Ollama')}
                            className={`p-1 rounded-md transition-all ${provider === 'Ollama' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20' : 'text-white/20'}`}
                            title="Usar Ollama (Local)"
                        >
                            <CpuChipIcon className="w-3.5 h-3.5" />
                        </button>
                    </div>

                    <button onClick={() => navigate('/ai')} className="p-2 hover:bg-white/5 rounded-lg text-white/40 hover:text-white transition-colors" title="Expandir">
                        <ArrowsPointingOutIcon className="w-4 h-4" />
                    </button>
                    <button onClick={() => setIsMinimized(true)} className="p-2 text-white/30 hover:text-white transition-all hover:bg-white/5 rounded-xl border border-transparent hover:border-white/5">
                        <MinusIcon className="w-5 h-5" />
                    </button>
                    <button onClick={() => setIsOpen(false)} className="p-2 text-white/30 hover:text-red-400 transition-all hover:bg-white/5 rounded-xl border border-transparent hover:border-white/5">
                        <XMarkIcon className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-5 space-y-6 bg-[radial-gradient(circle_at_50%_0%,rgba(79,70,229,0.05)_0%,transparent_50%)] custom-scrollbar">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                        <div className={`max-w-[85%] rounded-3xl px-4 py-3.5 text-sm shadow-xl ${msg.role === 'user'
                            ? 'bg-gradient-to-br from-indigo-600 to-indigo-700 border border-white/10 text-white rounded-br-none shadow-indigo-500/10'
                            : 'bg-white/5 border border-white/5 text-slate-300 rounded-bl-none'
                            }`}>

                            {/* Images */}
                            {msg.metadata?.imagePreviews && msg.metadata.imagePreviews.length > 0 && (
                                <div className="grid grid-cols-2 gap-2 mb-3">
                                    {msg.metadata.imagePreviews.map((src, i) => (
                                        <div key={i} className="aspect-square rounded-xl overflow-hidden border border-white/10">
                                            <img src={src} alt="Adjunto" className="w-full h-full object-cover" />
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Text */}
                            <p className="whitespace-pre-wrap leading-relaxed font-medium">
                                {msg.content.replace(/\*\*/g, '')}
                            </p>

                            {/* Sources Tags */}
                            {msg.metadata?.sources && msg.metadata.sources.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1">
                                    {msg.metadata.sources.map((source, idx) => (
                                        <span key={idx} className="text-[7px] bg-indigo-500/10 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-500/20 font-bold uppercase tracking-wider">
                                            {source.replace(' (NotebookLM)', '')}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {/* Assistant Branding Mini */}
                            {msg.role === 'assistant' && msg.id !== 'welcome' && (
                                <div className="mt-3 flex items-center gap-2 pt-2 border-t border-white/5 opacity-50">
                                    <CpuChipIcon className="w-3 h-3 text-indigo-400" />
                                    <span className="text-[8px] font-black uppercase tracking-[0.2em] text-indigo-400">AI Engine</span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white/5 border border-white/5 px-5 py-4 rounded-3xl rounded-bl-none flex items-center gap-3">
                            <div className="flex gap-1.5">
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" />
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-150" />
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-300" />
                            </div>
                            <span className="text-[9px] font-black uppercase tracking-widest text-indigo-400">Analizando</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} className="h-2" />
            </div>

            {/* Input Container */}
            <div className="p-6 bg-[#0B0F19] border-t border-white/5 flex-shrink-0 space-y-4">
                {/* Image Selection Previews */}
                {filePreviews.length > 0 && (
                    <div className="flex gap-3 px-1">
                        {filePreviews.map((src, i) => (
                            <div key={i} className="relative w-14 h-14 rounded-xl border border-indigo-500/50 overflow-hidden group shadow-lg">
                                <img src={src} alt="Preview" className="w-full h-full object-cover" />
                                <button onClick={clearFiles} className="absolute inset-0 bg-red-500/80 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                                    <TrashIcon className="w-5 h-5 text-white" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                <div className="flex items-end gap-3">
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className={`p-4 rounded-2xl transition-all border shrink-0 ${selectedFiles.length > 0 ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-400' : 'bg-white/5 border-white/5 text-white/30 hover:bg-white/10 hover:text-white'}`}
                    >
                        <PhotoIcon className="w-6 h-6" />
                    </button>
                    <input ref={fileInputRef} type="file" accept="image/*" multiple onChange={handleFileSelect} className="hidden" />

                    <div className="flex-1 bg-white/5 rounded-2xl border border-white/5 focus-within:border-indigo-500/30 transition-all flex items-center pr-2">
                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Consultar..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-white placeholder-white/20 resize-none py-3.5 px-4 custom-scrollbar leading-relaxed font-bold"
                            rows={1}
                            style={{ minHeight: '52px', maxHeight: '120px' }}
                        />
                        <button
                            onClick={handleSend}
                            disabled={isLoading || (!inputValue.trim() && selectedFiles.length === 0)}
                            className="p-3 bg-indigo-600 text-white rounded-xl shadow-lg shadow-indigo-900/40 hover:bg-indigo-500 disabled:opacity-25 transition-all active:scale-95 shrink-0"
                        >
                            <PaperAirplaneIcon className="w-5 h-5 -rotate-45" />
                        </button>
                    </div>
                </div>

                <p className="text-[9px] text-white/10 font-bold uppercase tracking-[0.3em] text-center pt-2">
                    Asistente IA Industrial Premium v1.0
                </p>
            </div>
        </div>
    );
}
