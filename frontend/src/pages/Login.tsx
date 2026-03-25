"use client";

import { useState } from 'react';
import { Logo } from '../components/Logo';
import {
    Eye,
    EyeOff,
    Lock,
    Mail,
    ArrowRight,
    Headphones,
    ShieldCheck,
    X,
    Phone,
    ExternalLink
} from 'lucide-react';

interface LoginProps {
    onSubmit: (credentials: { username: string; password: string }) => void;
    isLoading?: boolean;
    error?: string;
}

const COUNTRIES = [
    { code: 'CL', name: 'Chile', flag: '🇨🇱', flagPath: '/assets/flags/cl.png', color: 'from-red-500 to-blue-500', db: 'PRDPOSTVENTA_CL' },
    { code: 'PE', name: 'Perú', flag: '🇵🇪', flagPath: '/assets/flags/pe.png', color: 'from-red-500 to-red-600', db: 'PRDPOSTVENTA_PE' },
    { code: 'CO', name: 'Colombia', flag: '🇨🇴', flagPath: '/assets/flags/co.png', color: 'from-yellow-400 to-red-500', db: 'PRDPOSTVENTA_CO' }
];

export default function Login({ onSubmit, isLoading = false, error }: LoginProps) {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });
    const [selectedCountry, setSelectedCountry] = useState(COUNTRIES[0]);
    const [showPassword, setShowPassword] = useState(false);
    const [showSupportModal, setShowSupportModal] = useState(false);
    const [showSecurityModal, setShowSecurityModal] = useState(false);

    const handleCountrySelect = (country: typeof COUNTRIES[0]) => {
        setSelectedCountry(country);
        localStorage.setItem('country_code', country.code);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.username || !formData.password) return;

        // PRE-FLIGHT: Detect country from username suffix and set localStorage BEFORE request
        // This ensures the interceptor in api.js picks up the correct country header
        const lowerUser = formData.username.toLowerCase().trim();
        let detectedCountry = 'CL'; // Default

        if (lowerUser.endsWith('.pe')) {
            detectedCountry = 'PE';
        } else if (lowerUser.endsWith('.co')) {
            detectedCountry = 'CO';
        }

        console.log(`[Login] Auto-detecting country for ${lowerUser}: ${detectedCountry}`);
        localStorage.setItem('country_code', detectedCountry);

        onSubmit(formData);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleForgotPassword = () => {
        const subject = encodeURIComponent("Solicitud de Cambio de Contraseña - Sistema de Gestión de Incidencias");
        const body = encodeURIComponent(`Hola Jesús,\n\nSolicito apoyo para el cambio de mi contraseña en el Sistema de Gestión de Incidencias.\n\nDetalle de solicitud:\n- Usuario: ${formData.username || '[Escriba su usuario aquí]'}\n- Nueva contraseña deseada: [Escriba aquí la nueva contraseña que desea]\n\nQuedo atento a su colaboración.\n\nSaludos.`);
        window.location.href = `mailto:jdiaz@polifusion.cl?subject=${subject}&body=${body}`;
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden bg-[#020617] font-sans">

            {/* Modern Industrial IA Generated Background - AZUL BLUR OPTIMIZADO */}
            <div
                className="absolute inset-0 z-0 bg-cover bg-center transition-all duration-1000 scale-105"
                style={{
                    backgroundImage: `url('/assets/modern_industrial_bg.png')`,
                    filter: 'brightness(1.2) contrast(1.1) saturate(1.1)', // Brillo equilibrado para el tinte azul
                }}
            >
                {/* Cinematic Overlays - Azul Blur Profesional */}
                <div className="absolute inset-0 bg-slate-950/60"></div>
                <div className="absolute inset-0 bg-gradient-to-tr from-[#020617] via-blue-900/40 to-[#020617]/80"></div>
                <div className="absolute inset-0 opacity-[0.1] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>
                <div className="absolute inset-0 bg-radial-gradient from-transparent via-transparent to-slate-950/70"></div>
            </div>

            <div className="max-w-[480px] w-full px-6 relative z-10 animate-fade-in flex flex-col items-center">

                {/* Free Logo Concept with Futuristic Support Icon */}
                <div className="mb-10 text-center relative group flex flex-col items-center">
                    {/* Security Halo / Glow */}
                    <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-48 h-48 bg-blue-500/10 rounded-full blur-[90px] opacity-20 group-hover:opacity-40 transition-opacity duration-1000"></div>

                    {/* Security Icon Badge (Futuristic) */}
                    <div className="mb-5 relative group-hover:scale-110 transition-transform duration-700">
                        <div className="absolute inset-0 bg-blue-400 rounded-full blur-md opacity-20 animate-pulse"></div>
                        <div className="relative p-2.5 bg-slate-900/60 backdrop-blur-2xl border border-blue-500/30 rounded-full text-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.2)]">
                            <ShieldCheck size={18} className="animate-pulse" />
                        </div>
                    </div>

                    <div className="h-16 w-auto relative drop-shadow-[0_0_15px_rgba(255,255,255,0.15)] transform transition-all duration-1000 group-hover:scale-105">
                        <Logo variant="white" className="h-full w-auto" />
                    </div>
                </div>

                {/* Massive Industrial Login Card - PREMIUM GLASSMORPHISM */}
                <div className="w-full relative group/card">
                    <div className="absolute -inset-[1px] bg-gradient-to-r from-blue-500/20 via-white/10 to-indigo-500/20 rounded-[2.5rem] blur-[10px] opacity-40"></div>

                    <div className="relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-10 md:p-12 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)]">

                        <div className="text-center mb-10">
                            <h3 className="text-3xl font-black text-white italic tracking-tighter uppercase leading-none drop-shadow-md">Iniciar sesión</h3>
                            <div className="flex items-center justify-center gap-2 mt-4">
                                <span className="h-[1px] w-3 bg-blue-500/40"></span>
                                <p className="text-blue-200 text-[10px] font-bold uppercase tracking-[0.4em] leading-relaxed">
                                    Postventa Polifusión
                                </p>
                                <span className="h-[1px] w-3 bg-blue-500/40"></span>
                            </div>
                        </div>

                        <form className="space-y-6" onSubmit={handleSubmit}>
                            {error && (
                                <div className="bg-red-500/10 border border-red-500/20 p-3 rounded-xl flex items-center animate-shake">
                                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 mr-3 animate-pulse"></div>
                                    <p className="text-[9px] text-red-200 font-bold uppercase tracking-widest">{error}</p>
                                </div>
                            )}

                            <div className="space-y-5">
                                <div className="space-y-2">
                                    <label className="text-[9px] font-bold text-slate-300 uppercase tracking-[0.2em] ml-1">Usuario</label>
                                    <div className="relative group/input">
                                        <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-slate-400 group-focus-within/input:text-blue-400 transition-colors duration-300">
                                            <Mail size={16} />
                                        </div>
                                        <input
                                            name="username"
                                            type="text"
                                            required
                                            value={formData.username}
                                            onChange={handleChange}
                                            className="w-full bg-black/40 border border-white/10 focus:border-blue-500/50 rounded-2xl py-4 pl-12 pr-4 text-white text-sm outline-none transition-all placeholder:text-slate-500 font-bold tracking-tight shadow-inner"
                                            placeholder="usuario@polifusion.cl"
                                            disabled={isLoading}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[9px] font-bold text-slate-300 uppercase tracking-[0.2em] ml-1">Contraseña</label>
                                    <div className="relative group/input">
                                        <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-slate-400 group-focus-within/input:text-blue-400 transition-colors duration-300">
                                            <Lock size={16} />
                                        </div>
                                        <input
                                            name="password"
                                            type={showPassword ? 'text' : 'password'}
                                            required
                                            value={formData.password}
                                            onChange={handleChange}
                                            className="w-full bg-black/40 border border-white/10 focus:border-blue-500/50 rounded-2xl py-4 pl-12 pr-12 text-white text-sm outline-none transition-all placeholder:text-slate-500 font-bold tracking-tight shadow-inner"
                                            placeholder="••••••••"
                                            disabled={isLoading}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute inset-y-0 right-0 pr-5 flex items-center text-slate-500 hover:text-blue-400 transition-colors"
                                        >
                                            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end pr-1">
                                <button
                                    type="button"
                                    onClick={handleForgotPassword}
                                    className="text-[8px] font-bold text-slate-400 hover:text-white uppercase tracking-[0.2em] transition-all flex items-center gap-2 group/link"
                                >
                                    <ExternalLink size={9} className="group-hover/link:translate-y-[-1px] transition-transform" />
                                    ¿Olvidaste tu contraseña?
                                </button>
                            </div>

                            <div className="pt-2">
                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="w-full bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-600 text-white rounded-2xl py-4 px-8 font-black uppercase text-xs tracking-[0.4em] shadow-[0_10px_30px_rgba(29,78,216,0.2)] hover:shadow-blue-500/30 hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center group disabled:opacity-50 overflow-hidden relative"
                                >
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                                    {isLoading ? (
                                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white"></div>
                                    ) : (
                                        <>
                                            Acceder al Sistema
                                            <ArrowRight className="ml-3 h-5 w-5 transform transition-transform group-hover:translate-x-2" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>

                        {/* Separator */}
                        <div className="relative flex py-5 items-center opacity-10">
                            <div className="flex-grow border-t border-white"></div>
                            <span className="flex-shrink-0 mx-4 text-[9px] font-black text-white uppercase tracking-[0.5em]">Acceso Seguro</span>
                            <div className="flex-grow border-t border-white"></div>
                        </div>

                        {/* Footer Actions */}
                        <div className="flex justify-between items-center text-[9px] font-bold text-slate-400 uppercase tracking-widest pt-1">
                            <button
                                onClick={() => setShowSupportModal(true)}
                                className="flex items-center gap-2 hover:text-blue-400 transition-all group/support"
                            >
                                <Headphones size={13} className="group-hover/support:scale-110 transition-transform" />
                                Soporte Técnico
                            </button>
                            <button
                                onClick={() => setShowSecurityModal(true)}
                                className="flex items-center gap-2 hover:text-blue-400 transition-all group/security"
                            >
                                <ShieldCheck size={13} className="group-security:scale-110 transition-transform" />
                                Seguridad y App
                            </button>
                            <div className="flex items-center gap-2 opacity-30">
                                <ShieldCheck size={11} />
                                <span>v1.0</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Technical Label (Final Institutional Footer) - MODERN OPTIMIZED */}
                <div className="mt-8 pt-6 border-t border-white/5 flex flex-col items-center gap-1 opacity-40">
                    <div className="flex items-center gap-2">
                        <span className="h-[1px] w-6 bg-white/20"></span>
                        <span className="text-[10px] font-medium text-white/60 tracking-[0.2em] uppercase">© {new Date().getFullYear()}</span>
                        <span className="h-[1px] w-6 bg-white/20"></span>
                    </div>
                    <span className="text-[9px] font-black text-white/40 uppercase tracking-[0.4em] text-center ml-[0.4em] whitespace-nowrap">
                        Derechos reservados Polifusión S.A.
                    </span>
                </div>
            </div>

            {/* Modern Support Modal */}
            {showSupportModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in">
                    <div className="relative w-full max-w-sm bg-[#0f172a] border border-white/10 rounded-[2.5rem] p-8 shadow-2xl animate-scale-in">
                        <button
                            onClick={() => setShowSupportModal(false)}
                            className="absolute top-6 right-6 text-slate-500 hover:text-white transition-colors"
                        >
                            <X size={24} />
                        </button>
                        <div className="text-center mb-8">
                            <div className="w-16 h-16 bg-cyan-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-cyan-500/20">
                                <Headphones className="text-cyan-400 w-8 h-8" />
                            </div>
                            <h4 className="text-xl font-black text-white uppercase tracking-tighter">Ayuda y Soporte</h4>
                            <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mt-2 px-4">Centro de atención técnica para usuarios de la plataforma</p>
                        </div>

                        <div className="space-y-4">
                            <a
                                href="mailto:jdiaz@polifusion.cl"
                                className="flex items-center gap-4 p-5 bg-slate-900/50 hover:bg-slate-900 border border-white/5 rounded-2xl transition-all group/item"
                            >
                                <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover/item:scale-110 transition-transform">
                                    <Mail size={20} />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Correo Directo</span>
                                    <span className="text-sm font-bold text-white">jdiaz@polifusion.cl</span>
                                </div>
                            </a>

                            <a
                                href="tel:+56964258516"
                                className="flex items-center gap-4 p-5 bg-slate-900/50 hover:bg-slate-900 border border-white/5 rounded-2xl transition-all group/item"
                            >
                                <div className="p-3 bg-green-500/10 rounded-xl text-green-400 group-hover/item:scale-110 transition-transform">
                                    <Phone size={20} />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">WhatsApp / Llamada</span>
                                    <span className="text-sm font-bold text-white">+56 9 64258516</span>
                                </div>
                            </a>
                        </div>

                        <div className="mt-8 text-center">
                            <button
                                onClick={() => setShowSupportModal(false)}
                                className="text-[10px] font-black text-slate-500 hover:text-white uppercase tracking-[0.3em] transition-all"
                            >
                                Cerrar Ventana
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Modern Security & PWA Modal */}
            {showSecurityModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in">
                    <div className="relative w-full max-w-sm bg-[#0f172a] border border-white/10 rounded-[2.5rem] p-8 shadow-2xl animate-scale-in">
                        <button
                            onClick={() => setShowSecurityModal(false)}
                            className="absolute top-6 right-6 text-slate-500 hover:text-white transition-colors"
                        >
                            <X size={24} />
                        </button>
                        <div className="text-center mb-8">
                            <div className="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-blue-500/20">
                                <ShieldCheck className="text-blue-400 w-8 h-8" />
                            </div>
                            <h4 className="text-xl font-black text-white uppercase tracking-tighter">Seguridad y Aplicación</h4>
                            <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mt-2 px-4">Instala el certificado para habilitar la App Desktop</p>
                        </div>

                        <div className="space-y-4">
                            <a
                                href="/api/users/download-ca/"
                                className="flex items-center gap-4 p-5 bg-slate-900/50 hover:bg-slate-900 border border-white/5 rounded-2xl transition-all group/item"
                                download="Polifusion-CA.crt"
                            >
                                <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover/item:scale-110 transition-transform">
                                    <ShieldCheck size={20} />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Paso 1: Confianza</span>
                                    <span className="text-sm font-bold text-white">Descargar Root CA</span>
                                </div>
                            </a>

                            <div 
                                className="flex items-center gap-4 p-5 bg-slate-900/50 border border-white/5 rounded-2xl opacity-80 cursor-default"
                            >
                                <div className="p-3 bg-indigo-500/10 rounded-xl text-indigo-400">
                                    <ExternalLink size={20} />
                                </div>
                                <div className="flex flex-col text-left">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Paso 2: Instalación</span>
                                    <span className="text-[11px] font-medium text-slate-300">Usa el icono de instalación en la barra de direcciones tras instalar el certificado.</span>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 text-center bg-blue-500/5 p-4 rounded-xl border border-blue-500/10">
                            <p className="text-[9px] text-blue-300/80 font-bold uppercase tracking-[0.1em] leading-relaxed">
                                Tip: Instala el certificado en "Entidades de certificación raíz de confianza" en Windows.
                            </p>
                        </div>

                        <div className="mt-8 text-center text-[10px] font-black text-slate-500 hover:text-white uppercase tracking-[0.3em] transition-all cursor-pointer" onClick={() => setShowSecurityModal(false)}>
                            Cerrar Ventana
                        </div>
                    </div>
                </div>
            )}

            {/* Custom Animations in CSS Style */}
            <style dangerouslySetInnerHTML={{
                __html: `
        @keyframes fade-in { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scale-in { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        @keyframes slow-zoom { from { transform: scale(1.05); } to { transform: scale(1.15); } }
        .animate-fade-in { animation: fade-in 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        .animate-scale-in { animation: scale-in 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        .animate-slow-zoom { animation: slow-zoom 30s linear infinite alternate; }
        .animate-shake { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }
        .bg-radial-gradient { background: radial-gradient(circle, var(--tw-gradient-from), var(--tw-gradient-to)); }
        @keyframes shake {
          10%, 90% { transform: translate3d(-1px, 0, 0); }
          20%, 80% { transform: translate3d(2px, 0, 0); }
          30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
          40%, 60% { transform: translate3d(4px, 0, 0); }
        }
      ` }} />
        </div>
    );
}
