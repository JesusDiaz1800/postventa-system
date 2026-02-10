import { useState, useEffect, useRef } from 'react';
import {
    XMarkIcon,
    PaperAirplaneIcon,
    MinusIcon,
    SparklesIcon,
    ArrowPathIcon,
    PhotoIcon,
    UserCircleIcon,
    ChatBubbleOvalLeftEllipsisIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api, aiAgentsAPI } from '../services/api';
import { formatAnalysisResult } from '../utils/aiUtils';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    metadata?: {
        confidence?: number;
        reasoning?: string;
        imagePreview?: string;
        sources?: string[];
    };
}

const STORAGE_KEY = 'ai_floating_chat_history';

export function FloatingAIChat() {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { showError } = useNotifications();

    useEffect(() => {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                setMessages(JSON.parse(stored));
            } else {
                setMessages([{
                    id: 'welcome',
                    role: 'assistant',
                    content: '¡Hola! Soy tu asistente de Polifusión. ¿En qué puedo ayudarte hoy?',
                    timestamp: new Date().toISOString()
                }]);
            }
        } catch (e) {
            console.error('Error loading chat history:', e);
        }
    }, []);

    useEffect(() => {
        if (messages.length > 0) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
        }
    }, [messages]);

    useEffect(() => {
        if (isOpen && !isMinimized) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isOpen, isMinimized]);

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
            content: inputValue.trim() || '[Imagen adjunta]',
            timestamp: new Date().toISOString(),
            metadata: selectedImage ? { imagePreview: imagePreview || undefined } : undefined
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsProcessing(true);

        try {
            let responseData;
            if (selectedImage) {
                const formData = new FormData();
                formData.append('image', selectedImage);
                formData.append('query', inputValue || 'Analiza esta imagen');

                const result = await api.post('/ai/analyze-image/', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                });

                responseData = {
                    response: result.data.response || result.data.analysis || 'Análisis completado',
                    confidence: result.data.confidence,
                    reasoning: result.data.reasoning
                };
            } else {
                const result = await aiAgentsAPI.query({ query: userMessage.content });
                responseData = result.data;
            }

            let responseContent = typeof responseData.response === 'string'
                ? responseData.response
                : JSON.stringify(responseData.response || responseData.error || 'Sin respuesta', null, 2);

            responseContent = formatAnalysisResult(responseContent);

            const assistantMessage: ChatMessage = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: responseContent,
                timestamp: new Date().toISOString(),
                metadata: {
                    confidence: responseData.confidence,
                    reasoning: responseData.reasoning,
                    sources: responseData.sources
                }
            };

            setMessages(prev => [...prev, assistantMessage]);
            if (!isOpen && !isMinimized) setUnreadCount(prev => prev + 1);
            clearImage();

        } catch (error: any) {
            const errorMsg: ChatMessage = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: `Error del sistema: ${error.response?.data?.error || error.message || 'Conexión interrumpida'}`,
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => { setIsOpen(true); setIsMinimized(false); setUnreadCount(0); }}
                className="fixed bottom-6 right-6 w-14 h-14 bg-purple-600 rounded-full shadow-lg flex items-center justify-center text-white hover:bg-purple-700 hover:scale-110 transition-all z-50 group"
            >
                <ChatBubbleOvalLeftEllipsisIcon className="w-8 h-8" />
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full text-xs flex items-center justify-center font-bold border-2 border-white">
                        {unreadCount}
                    </span>
                )}
            </button>
        );
    }

    if (isMinimized) {
        return (
            <div className="fixed bottom-6 right-6 w-64 bg-white border border-gray-200 rounded-xl z-50 overflow-hidden shadow-xl">
                <div className="p-3 bg-purple-600 flex items-center justify-between">
                    <span className="text-white text-sm font-bold flex items-center gap-2">
                        <SparklesIcon className="w-4 h-4" /> Asistente IA
                    </span>
                    <div className="flex items-center gap-2">
                        <button onClick={() => setIsMinimized(false)} className="text-purple-100 hover:text-white transition-colors">
                            <ArrowPathIcon className="w-4 h-4" />
                        </button>
                        <button onClick={() => setIsOpen(false)} className="text-purple-100 hover:text-white transition-colors">
                            <XMarkIcon className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 w-[380px] h-[580px] max-h-[80vh] bg-white border border-gray-200 z-50 flex flex-col rounded-2xl overflow-hidden shadow-2xl animate-scale-in">
            {/* Header */}
            <div className="px-5 py-4 bg-purple-600 flex items-center justify-between flex-shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                        <SparklesIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h3 className="text-white font-bold text-sm">Asistente Polifusión</h3>
                        <div className="flex items-center gap-1.5">
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                            <p className="text-purple-100 text-[10px] uppercase font-bold tracking-wider">Online</p>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={() => setIsMinimized(true)} className="p-1.5 text-purple-100 hover:text-white transition-colors hover:bg-white/10 rounded-lg">
                        <MinusIcon className="w-5 h-5" />
                    </button>
                    <button onClick={() => setIsOpen(false)} className="p-1.5 text-purple-100 hover:text-white transition-colors hover:bg-white/10 rounded-lg">
                        <XMarkIcon className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[85%] space-y-1 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                            <div className={`inline-block px-4 py-3 rounded-2xl shadow-sm text-sm ${msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-tr-none'
                                : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
                                }`}>
                                {msg.metadata?.imagePreview && (
                                    <div className="mb-2">
                                        <img src={msg.metadata.imagePreview} alt="Adjunto" className="w-full h-auto max-h-40 object-cover rounded-lg" />
                                    </div>
                                )}
                                <div className="leading-relaxed whitespace-pre-wrap">
                                    {msg.content}
                                </div>
                                {msg.role === 'assistant' && msg.metadata?.sources && msg.metadata.sources.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-gray-100">
                                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Fuentes:</p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {msg.metadata.sources.map((source, idx) => (
                                                <span key={idx} className="text-[9px] px-2 py-0.5 bg-gray-50 text-gray-500 rounded border border-gray-100">
                                                    {source.split(' - ')[0]}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                            <p className="text-[10px] text-gray-400 px-1">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                        </div>
                    </div>
                ))}
                {isProcessing && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm">
                            <div className="flex gap-1.5">
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '200ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '400ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100 flex-shrink-0 space-y-3">
                {imagePreview && (
                    <div className="relative inline-block border border-gray-200 p-1 rounded-lg bg-gray-50">
                        <img src={imagePreview} alt="Preview" className="h-16 rounded cursor-pointer" />
                        <button onClick={clearImage} className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center shadow-md">
                            <XMarkIcon className="w-4 h-4" />
                        </button>
                    </div>
                )}

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="p-2.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all"
                    >
                        <PhotoIcon className="w-6 h-6" />
                    </button>
                    <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />

                    <div className="flex-1">
                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Escribe un mensaje..."
                            className="w-full px-4 py-3 bg-gray-100 border-none focus:ring-2 focus:ring-blue-500 rounded-xl text-sm text-gray-900 placeholder-gray-500 resize-none transition-all scrollbar-hide"
                            rows={1}
                            style={{ minHeight: '44px', maxHeight: '120px' }}
                        />
                    </div>

                    <button
                        onClick={handleSend}
                        disabled={(!inputValue.trim() && !selectedImage) || isProcessing}
                        className="p-3 bg-purple-600 text-white rounded-xl shadow-md hover:bg-purple-700 disabled:opacity-50 transition-all transform active:scale-95"
                    >
                        <PaperAirplaneIcon className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
