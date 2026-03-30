import { useState, useCallback, useEffect } from 'react';
import { api, aiAgentsAPI } from '../services/api';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
    metadata?: {
        confidence?: number;
        reasoning?: string;
        imagePreviews?: string[]; // Array of base64 strings or URLs
        analysisData?: any;
        reportHtml?: string;
        sources?: string[];
    };
}

interface UseAIChatReturn {
    messages: ChatMessage[];
    isLoading: boolean;
    error: string | null;
    sendMessage: (content: string, files?: File[]) => Promise<void>;
    generateReport: () => Promise<void>;
    clearChat: () => void;
    lastAnalysisData: any | null;
    setLastAnalysisData: (data: any) => void;
    refreshHistory: () => void;
    provider: 'Gemini' | 'Ollama';
    setProvider: (provider: 'Gemini' | 'Ollama') => void;
}

export const useAIChat = (storageKey: string = 'ai_chat_history_v3'): UseAIChatReturn => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lastAnalysisData, setLastAnalysisData] = useState<any | null>(null);
    const [provider, setProvider] = useState<'Gemini' | 'Ollama'>('Gemini');

    // Load from storage on mount
    useEffect(() => {
        try {
            const stored = localStorage.getItem(storageKey);
            if (stored) {
                const parsed = JSON.parse(stored);
                setMessages(parsed);
                // Try to recover last analysis data from history
                const lastAssistantMsg = [...parsed].reverse().find((m: ChatMessage) => m.role === 'assistant' && m.metadata?.analysisData);
                if (lastAssistantMsg) {
                    setLastAnalysisData(lastAssistantMsg.metadata.analysisData);
                }
            } else {
                setMessages([{
                    id: 'welcome',
                    role: 'assistant',
                    content: '¡Hola! Soy tu asistente técnico avanzado. Puedo analizar múltiples imágenes de fallas, generar reportes técnicos y responder consultas sobre normativas.',
                    timestamp: new Date().toISOString()
                }]);
            }
        } catch (e) {
            console.error("Error loading chat history:", e);
        }
    }, [storageKey]);

    // Save to storage on change
    // Save to storage on change
    useEffect(() => {
        if (messages.length > 0) {
            try {
                // Optimization: Create a clean copy for storage
                // 1. Strip base64 image previews (too large for localStorage)
                // 2. Keep only the last 50 messages to stay within limits
                const messagesToSave = messages.slice(-50).map(msg => ({
                    ...msg,
                    metadata: {
                        ...msg.metadata,
                        imagePreviews: [] // Don't persist base64 images
                    }
                }));
                localStorage.setItem(storageKey, JSON.stringify(messagesToSave));
            } catch (e) {
                console.warn("LocalStorage quota exceeded, attempting to save minimal history...", e);
                try {
                    // Fallback: Save only last 10 text-only messages
                    const minimalMessages = messages.slice(-10).map(msg => ({
                        id: msg.id,
                        role: msg.role,
                        content: msg.content,
                        timestamp: msg.timestamp,
                        // Strip all metadata in worst case
                    }));
                    localStorage.setItem(storageKey, JSON.stringify(minimalMessages));
                } catch (retryError) {
                    console.error("Critical storage error: could not save chat history.", retryError);
                }
            }
        }
    }, [messages, storageKey]);

    const sendMessage = useCallback(async (content: string, files: File[] = []) => {
        if (!content.trim() && files.length === 0) return;

        setIsLoading(true);
        setError(null);

        // Create User Message
        const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'user',
            content: content,
            timestamp: new Date().toISOString(),
            metadata: {
                imagePreviews: []
            }
        };

        // Generate Previews for UI
        if (files.length > 0) {
            const promises = files.map(file => new Promise<string>((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target?.result as string);
                reader.readAsDataURL(file);
            }));
            userMessage.metadata!.imagePreviews = await Promise.all(promises);
            // Default text if empty
            if (!userMessage.content) userMessage.content = `[${files.length} Imágenes adjuntas]`;
        }

        setMessages(prev => [...prev, userMessage]);

        try {
            let responseData;

            if (files.length > 0) {
                // Image Analysis (Multi-image) using standard API
                const result = await aiAgentsAPI.analyzeImage(files, content, provider);
                responseData = result.data;
            } else {
                // Text Query
                const result = await aiAgentsAPI.query({ 
                    query: content,
                    provider: provider 
                });
                responseData = result.data;
            }

            // Process Assistant Response
            const assistantMessage: ChatMessage = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: responseData.response || "Análisis completado.",
                timestamp: new Date().toISOString(),
                metadata: {
                    confidence: responseData.confidence,
                    reasoning: responseData.reasoning,
                    sources: responseData.sources,
                    analysisData: responseData.analysis_data // Store structured data for reports
                }
            };

            setLastAnalysisData(responseData.analysis_data || null);
            setMessages(prev => [...prev, assistantMessage]);

        } catch (err: any) {
            console.error("AI Error:", err);
            const errorMsg = err.response?.data?.error || err.message || "Error de conexión";
            setError(errorMsg);
            setMessages(prev => [...prev, {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: `Error: ${errorMsg}`,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const generateReport = useCallback(async () => {
        if (!lastAnalysisData && messages.length < 2) {
            setError("No hay suficientes datos para generar un reporte.");
            return;
        }

        setIsLoading(true);
        try {
            const payload = {
                analysis_data: lastAnalysisData,
                chat_history: messages.slice(-10) // Send context
            };

            const response = await aiAgentsAPI.generateReport(payload);

            if (response.data.success) {
                const reportMsg: ChatMessage = {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: "He generado el reporte técnico solicitado:",
                    timestamp: new Date().toISOString(),
                    metadata: {
                        reportHtml: response.data.report_html
                    }
                };
                setMessages(prev => [...prev, reportMsg]);
            }

        } catch (err: any) {
            console.error("Report Gen Error:", err);
            setError("Error al generar reporte: " + (err.response?.data?.error || err.message));
        } finally {
            setIsLoading(false);
        }
    }, [lastAnalysisData, messages]);

    const clearChat = useCallback(() => {
        setMessages([{
            id: 'welcome',
            role: 'assistant',
            content: 'Chat reiniciado. ¿En qué puedo ayudarte?',
            timestamp: new Date().toISOString()
        }]);
        setLastAnalysisData(null);
        localStorage.removeItem(storageKey);
    }, [storageKey]);

    const refreshHistory = useCallback(() => {
        try {
            const stored = localStorage.getItem(storageKey);
            if (stored) {
                setMessages(JSON.parse(stored));
            }
        } catch (e) {
            console.error("Error reloading chat history:", e);
        }
    }, [storageKey]);

    return {
        messages,
        isLoading,
        error,
        sendMessage,
        generateReport,
        clearChat,
        lastAnalysisData,
        setLastAnalysisData,
        refreshHistory,
        provider,
        setProvider
    };
};
