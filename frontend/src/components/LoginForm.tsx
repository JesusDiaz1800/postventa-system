"use client";

import { useState } from 'react';
import { Logo } from './Logo';
import { Eye, EyeOff, Lock, User, AlertCircle, ArrowRightIcon, ShieldCheck } from 'lucide-react';

interface LoginFormProps {
  onSubmit: (credentials: { username: string; password: string }) => void;
  isLoading?: boolean;
  error?: string;
}

export function LoginForm({ onSubmit, isLoading = false, error }: LoginFormProps) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username || !formData.password) return;
    onSubmit(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#020617]">
      {/* High-Impact Cinematic Industrial Background */}
      <div
        className="absolute inset-0 z-0 select-none pointer-events-none bg-cover bg-center"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1565191999001-551c187427bb?q=80&w=2070&auto=format&fit=crop')`, // Hard industrial sparks/factory
        }}
      >
        {/* Deep Industrial Overlays */}
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-[2px]"></div>
        <div className="absolute inset-0 bg-gradient-to-tr from-[#020617] via-transparent to-[#020617]/40"></div>

        {/* Scanline Effect (Industrial Tech Feel) */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.03] overflow-hidden">
          <div className="absolute inset-0 w-full h-full bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(255,255,255,0.5)_4px)]"></div>
        </div>

        {/* Dynamic Glows */}
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-blue-600/10 rounded-full blur-[100px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-cyan-600/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="max-w-[440px] w-full px-6 relative z-10 animate-fade-in flex flex-col items-center">

        {/* Premium Branding Header */}
        <div className="mb-8 text-center relative">
          <div className="relative mx-auto w-16 h-16 mb-6">
            <div className="absolute -inset-2 bg-blue-500/20 rounded-2xl blur-lg animate-pulse"></div>
            <div className="relative h-full w-full bg-[#0f172a] border border-white/10 rounded-2xl flex items-center justify-center shadow-2xl">
              <ShieldCheck className="text-blue-400 w-8 h-8" />
            </div>
          </div>
          <div className="flex items-center justify-center">
            <Logo className="h-10 w-auto" variant="white" />
          </div>
        </div>

        {/* Industrial Massive Login Card */}
        <div className="w-full relative group">
          {/* Intense Outer Glow (Senior Finish) */}
          <div className="absolute -inset-[2px] bg-gradient-to-r from-blue-600/40 via-cyan-400/20 to-indigo-600/40 rounded-[2rem] blur-[8px] opacity-30 group-hover:opacity-50 transition-opacity"></div>

          <div className="relative bg-[#0f172a]/95 backdrop-blur-3xl border border-white/10 rounded-[2rem] p-10 md:p-14 shadow-[0_30px_60px_-15px_rgba(0,0,0,0.6)]">

            <div className="text-center mb-10">
              <h3 className="text-3xl font-black text-white italic tracking-tighter uppercase">Identificación</h3>
              <div className="h-1 w-12 bg-blue-500 mx-auto mt-2 rounded-full shadow-[0_0_10px_#3b82f6]"></div>
              <p className="text-slate-400 text-[9px] font-black uppercase tracking-[0.3em] mt-5 leading-relaxed opacity-80">
                Sistema de Gestión de Incidencias Postventa
              </p>
            </div>

            <form className="space-y-7" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex items-center animate-shake">
                  <AlertCircle className="h-5 w-5 text-red-500 mr-3 flex-shrink-0" />
                  <p className="text-[10px] text-red-100 font-bold uppercase tracking-widest">{error}</p>
                </div>
              )}

              <div className="space-y-6">
                <div className="space-y-2.5">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Terminal de Acceso</label>
                  <div className="relative group/input">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600 group-focus-within/input:text-blue-400 transition-colors">
                      <User size={18} />
                    </div>
                    <input
                      name="username"
                      type="text"
                      required
                      value={formData.username}
                      onChange={handleChange}
                      className="w-full bg-black/40 border border-white/5 focus:border-blue-500/50 rounded-xl py-4 pl-12 pr-4 text-white text-sm outline-none transition-all placeholder:text-slate-800 font-bold tracking-tight"
                      placeholder="usuario@polifusion.cl"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div className="space-y-2.5">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Código de Seguridad</label>
                  <div className="relative group/input">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-600 group-focus-within/input:text-blue-400 transition-colors">
                      <Lock size={18} />
                    </div>
                    <input
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.password}
                      onChange={handleChange}
                      className="w-full bg-black/40 border border-white/5 focus:border-blue-500/50 rounded-xl py-4 pl-12 pr-12 text-white text-sm outline-none transition-all placeholder:text-slate-800 font-bold tracking-tight"
                      placeholder="••••••••"
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-700 hover:text-blue-400 transition-colors"
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pr-1">
                <button type="button" className="text-[9px] font-black text-slate-600 hover:text-white uppercase tracking-[0.2em] transition-all">
                  Restablecer Acceso
                </button>
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-700 via-blue-600 to-blue-500 text-white rounded-xl py-4.5 px-8 font-black uppercase text-xs tracking-[0.3em] shadow-[0_15px_30px_rgba(29,78,216,0.3)] hover:shadow-blue-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center group disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white"></div>
                  ) : (
                    <>
                      Validar Entrada
                      <ArrowRightIcon className="ml-3 h-5 w-5 transform transition-transform group-hover:translate-x-1" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Technical Label (Authentic Senior Finish) */}
        <div className="mt-12 flex flex-col items-center gap-2 opacity-30">
          <div className="h-px w-20 bg-gradient-to-r from-transparent via-white to-transparent"></div>
          <span className="text-[8px] font-black text-white uppercase tracking-[0.5em]">Polifusión S.A. &copy; {new Date().getFullYear()}</span>
        </div>
      </div>
    </div>
  );
}
