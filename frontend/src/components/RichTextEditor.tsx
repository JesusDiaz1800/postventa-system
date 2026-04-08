import React, { useState, useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import Image from '@tiptap/extension-image';
import Placeholder from '@tiptap/extension-placeholder';
import { api } from '../services/api';
import {
    BoldIcon,
    ItalicIcon,
    UnderlineIcon,
    ListBulletIcon,
    PhotoIcon,
    SparklesIcon,
    CheckCircleIcon,
    ArrowPathIcon,
    ArrowsRightLeftIcon,
    ClipboardDocumentIcon,
    XMarkIcon,
} from '@heroicons/react/24/outline';

const RichTextEditor = ({
    value = '',
    onChange,
    placeholder = 'Escriba aquí...',
    label = '',
    showAI = true,
    context = {}
}) => {
    const [isAILoading, setIsAILoading] = useState(false);
    const [showAIPanel, setShowAIPanel] = useState(false);
    const [originalText, setOriginalText] = useState('');
    const [improvedText, setImprovedText] = useState('');
    const [aiMode, setAiMode] = useState('improve');

    const editor = useEditor({
        extensions: [
            StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
            Underline,
            TextAlign.configure({ types: ['heading', 'paragraph'] }),
            Image.configure({ inline: true, allowBase64: true }),
            Placeholder.configure({ placeholder }),
        ],
        content: value,
        onUpdate: ({ editor }) => onChange?.(editor.getHTML()),
    });

    const handleAIImprove = useCallback(async () => {
        if (!editor) return;
        const text = editor.getText();
        if (!text || text.length < 10) {
            alert('Escriba al menos 10 caracteres para mejorar');
            return;
        }
        setOriginalText(text);
        setImprovedText('');
        setAiMode('improve');
        setShowAIPanel(true);
        setIsAILoading(true);
        try {
            const response = await api.post('/ai/writing/improve/', { text });
            setImprovedText(response.data?.improved_text || 'Error: Configure GEMINI_API_KEY');
        } catch (error) {
            if (error.response?.status === 429) {
                const resetTime = error.response.data?.next_reset ? new Date(error.response.data.next_reset).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'mañana';
                setImprovedText(`Límite de cuota alcanzado. Se restablecerá a las ${resetTime}. El sistema está usando el motor local básico.`);
            } else {
                setImprovedText('Error al procesar con IA. Por favor, verifique su configuración.');
            }
        } finally {
            setIsAILoading(false);
        }
    }, [editor]);

    const handleAIFix = useCallback(async () => {
        if (!editor) return;
        const text = editor.getText();
        if (!text) return;
        setOriginalText(text);
        setImprovedText('');
        setAiMode('fix');
        setShowAIPanel(true);
        setIsAILoading(true);
        try {
            const response = await api.post('/ai/writing/fix/', { text });
            setImprovedText(response.data?.fixed_text || 'Error: Configure GEMINI_API_KEY');
        } catch (error) {
            if (error.response?.status === 429) {
                const resetTime = error.response.data?.next_reset ? new Date(error.response.data.next_reset).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'mañana';
                setImprovedText(`Límite de cuota alcanzado. Se restablecerá a las ${resetTime}. El sistema está usando el motor local básico.`);
            } else {
                setImprovedText('Error al procesar con IA. Por favor, verifique su configuración.');
            }
        } finally {
            setIsAILoading(false);
        }
    }, [editor]);

    const handleAIGenerate = useCallback(async () => {
        setOriginalText(`Generando para:\n• Cliente: ${context.client_name || 'N/A'}\n• Proyecto: ${context.project_name || 'N/A'}`);
        setImprovedText('');
        setAiMode('generate');
        setShowAIPanel(true);
        setIsAILoading(true);
        try {
            const response = await api.post('/ai/writing/generate-report/', context);
            setImprovedText(response.data?.generated_content || 'Error: Configure GEMINI_API_KEY');
        } catch (error) {
            if (error.response?.status === 429) {
                const resetTime = error.response.data?.next_reset ? new Date(error.response.data.next_reset).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'mañana';
                setImprovedText(`Límite de cuota alcanzado. Se restablecerá a las ${resetTime}. El sistema está usando el motor local básico.`);
            } else {
                setImprovedText('Error al procesar con IA. Por favor, verifique su configuración.');
            }
        } finally {
            setIsAILoading(false);
        }
    }, [context]);

    const applyImprovedText = () => {
        if (improvedText && editor) {
            editor.commands.setContent(`<p>${improvedText.replace(/\n/g, '</p><p>')}</p>`);
            setShowAIPanel(false);
        }
    };

    const copyToClipboard = (text) => navigator.clipboard.writeText(text);

    const insertImage = useCallback(() => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = e.target.files?.[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => editor?.chain().focus().setImage({ src: event.target?.result, alt: file.name }).run();
                reader.readAsDataURL(file);
            }
        };
        input.click();
    }, [editor]);

    if (!editor) return <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />;

    const ToolbarButton = ({ onClick, active, disabled, children, title }) => (
        <button type="button" onClick={onClick} disabled={disabled} title={title}
            className={`p-2 rounded hover:bg-gray-100 ${active ? 'bg-blue-100 text-blue-600' : 'text-gray-600'} ${disabled ? 'opacity-50' : ''}`}>
            {children}
        </button>
    );

    return (
        <div className="border border-gray-300 rounded-xl overflow-hidden bg-white shadow-sm">
            {label && <div className="px-4 py-2 bg-gray-50 border-b"><label className="text-sm font-medium text-gray-700">{label}</label></div>}

            {/* Toolbar */}
            <div className="flex flex-wrap items-center gap-1 p-2 border-b bg-gray-50">
                <div className="flex items-center gap-1 border-r pr-2 mr-2">
                    <ToolbarButton onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive('bold')} title="Negrita"><BoldIcon className="h-4 w-4" /></ToolbarButton>
                    <ToolbarButton onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive('italic')} title="Cursiva"><ItalicIcon className="h-4 w-4" /></ToolbarButton>
                    <ToolbarButton onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive('underline')} title="Subrayado"><UnderlineIcon className="h-4 w-4" /></ToolbarButton>
                </div>
                <div className="flex items-center gap-1 border-r pr-2 mr-2">
                    <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} active={editor.isActive('heading', { level: 2 })} title="Título"><span className="font-bold text-sm">H</span></ToolbarButton>
                    <ToolbarButton onClick={() => editor.chain().focus().toggleBulletList().run()} active={editor.isActive('bulletList')} title="Lista"><ListBulletIcon className="h-4 w-4" /></ToolbarButton>
                    <ToolbarButton onClick={insertImage} title="Imagen"><PhotoIcon className="h-4 w-4" /></ToolbarButton>
                </div>
                {showAI && (
                    <div className="flex items-center gap-1 ml-auto">
                        <button type="button" onClick={handleAIImprove} disabled={isAILoading}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50">
                            <SparklesIcon className="h-3.5 w-3.5" /> Mejorar
                        </button>
                        <button type="button" onClick={handleAIFix} disabled={isAILoading}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50">
                            <CheckCircleIcon className="h-3.5 w-3.5" /> Corregir
                        </button>
                        <button type="button" onClick={handleAIGenerate} disabled={isAILoading}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50">
                            📝 Generar
                        </button>
                    </div>
                )}
            </div>

            {/* AI Side-by-Side Panel */}
            {showAIPanel && (
                <div className="border-b">
                    <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-purple-50 to-blue-50">
                        <h3 className="text-sm font-semibold text-purple-800">
                            {aiMode === 'improve' ? '✨ Mejora de Redacción' : aiMode === 'fix' ? '✅ Corrección' : '📝 Generación'}
                        </h3>
                        <button onClick={() => setShowAIPanel(false)} className="p-1 text-gray-500 hover:text-gray-700"><XMarkIcon className="h-5 w-5" /></button>
                    </div>
                    <div className="grid grid-cols-2 divide-x">
                        <div className="p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-gray-500 uppercase">📄 Original</span>
                                <button onClick={() => copyToClipboard(originalText)} className="p-1 text-gray-400 hover:text-gray-600"><ClipboardDocumentIcon className="h-4 w-4" /></button>
                            </div>
                            <div className="min-h-[100px] max-h-[180px] overflow-y-auto p-3 bg-gray-50 rounded text-sm whitespace-pre-wrap">{originalText}</div>
                        </div>
                        <div className="p-4 bg-purple-50/30">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-purple-600 uppercase">✨ Mejorado</span>
                                <button onClick={() => copyToClipboard(improvedText)} disabled={!improvedText} className="p-1 text-purple-400 hover:text-purple-600"><ClipboardDocumentIcon className="h-4 w-4" /></button>
                            </div>
                            <div className="min-h-[100px] max-h-[180px] overflow-y-auto p-3 bg-white rounded text-sm whitespace-pre-wrap border border-purple-100">
                                {isAILoading ? (
                                    <div className="flex items-center justify-center h-full"><ArrowPathIcon className="h-5 w-5 text-purple-500 animate-spin" /><span className="ml-2 text-purple-600">Procesando...</span></div>
                                ) : improvedText || 'Esperando...'}
                            </div>
                        </div>
                    </div>
                    {improvedText && !isAILoading && (
                        <div className="flex justify-center gap-3 px-4 py-3 bg-gray-50 border-t">
                            <button onClick={() => setShowAIPanel(false)} className="px-4 py-2 text-sm text-gray-600">Cancelar</button>
                            <button onClick={applyImprovedText} className="flex items-center gap-2 px-5 py-2 text-sm font-medium rounded-lg bg-purple-600 text-white hover:bg-purple-700">
                                <ArrowsRightLeftIcon className="h-4 w-4" /> Aplicar
                            </button>
                        </div>
                    )}
                </div>
            )}

            <EditorContent editor={editor} className="prose prose-sm max-w-none p-4 min-h-[150px]" />
        </div>
    );
};

export default RichTextEditor;
