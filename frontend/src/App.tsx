import { useEffect, useState, useMemo, lazy, Suspense } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence, motion } from 'framer-motion';

// PWA Components (keep eager - needed immediately)
import PWAInstaller from './components/PWAInstaller';
import PWAUpdate from './components/PWAUpdate';
// OfflineIndicator removed
import { PWAProvider } from './contexts/PWAContext'; // Import Provider

// Core Components (keep eager - needed for layout)
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Sidebar';
import React from 'react';
import Login from './pages/Login';
import { LoadingSpinner } from './components/LoadingSpinner';
import { Logo } from './components/Logo';
import { ErrorBoundary } from './components/ErrorBoundary';

// Global utilities
import { GlobalSearch } from './components/GlobalSearch';

// Pages - Direct imports to avoid Suspense hook issues
import AuditPage from './pages/AuditPage';
import Dashboard from './pages/Dashboard';
import QuickActions from './pages/QuickActions';
import Users from './pages/Users';
import VisitReportsPage from './pages/VisitReportsPage';
import VisitReportForm from './pages/VisitReportForm';
import VisitReportPreview from './pages/VisitReportPreview';
import ScheduleVisitPage from './pages/ScheduleVisitPage';

// Hooks
import { useAuth } from './hooks/useAuth';

// Utils
import { brandConfig } from './config/brand';

// Loading fallback component - CINEMATIC VERSION
const PageLoader = () => (
  <div className="flex flex-col items-center justify-center min-h-[400px] space-y-8 animate-fade-in">
    <div className="relative group">
      {/* Decorative Halo */}
      <div className="absolute -inset-10 bg-blue-500/10 rounded-full blur-3xl opacity-20 animate-pulse"></div>

      {/* Logo with pulse */}
      <div className="h-24 w-auto relative transform transition-all duration-1000 animate-float drop-shadow-[0_0_15px_rgba(59,130,246,0.2)]">
        <Logo className="h-full w-auto" />
      </div>
    </div>

    <div className="flex flex-col items-center gap-3">
      <div className="flex gap-1.5">
        <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce"></div>
      </div>
      <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.6em] animate-pulse ml-[0.6em]">
        Cargando Sistema
      </p>
    </div>
  </div>
);

function App() {
  const { user, isLoading, login, getUserDisplayName } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => window.innerWidth >= 1024);
  const navigate = useNavigate();
  const location = useLocation();
  const scrollRef = useEffect(() => {
    const mainContainer = document.getElementById('main-scroll-container');
    if (mainContainer) {
      mainContainer.scrollTo({ top: 0, behavior: 'instant' });
    }
  }, [location.pathname]);

  // Handle sidebar responsive behavior
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsSidebarOpen(true);
      } else {
        setIsSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Set document title
  useEffect(() => {
    document.title = "SERTEC - Sistema de Visitas en Terreno";
  }, []);

  // Redirect logic handled directly by useAuth during login and Navigate components in Routes

  // No forzar modo oscuro
  /* useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []); */

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <PageLoader />
      </div>
    );
  }

  if (!user) {
    return <Login onSubmit={login} isLoading={isLoading} />;
  }

  const isDashboard = location.pathname === '/dashboard';
  const isLanding = location.pathname === '/quick-actions';
  const isVisitForm = location.pathname.startsWith('/visit-report-form') || location.pathname.includes('/preview');

  return (
    <div className={`min-h-screen relative transition-colors duration-500 ${isLanding ? 'bg-[#030014] text-white' : 'bg-slate-50/30 text-slate-900'}`}>
      {/* Capas de Fondo Premium - Condicionales */}
      {isLanding ? (
        <>
          <div className="mesh-gradient-bg opacity-40" />
          <div className="tech-grid-overlay opacity-20" />
        </>
      ) : (
        <>
          <div className="light-mesh-bg" />
          <div className="absolute inset-0 bg-white/40 pointer-events-none backdrop-blur-[2px]" />
        </>
      )}

      <ErrorBoundary>
          {/* Global Search Overlay - Ctrl+K */}
          {/* GlobalSearch is now wrapped in Suspense and moved inside the flex container */}

          <div className="flex relative z-10">
            <GlobalSearch />
            
            {/* Ocultar Sidebar en QuickActions y Formulario para máxima inmersión */}
            {!isLanding && !isVisitForm && (
              <MemoizedSidebar
                currentPath={location.pathname}
                onNavigate={(path) => navigate(path)}
                userName={getUserDisplayName()}
                userRole={user.role}
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
              />
            )}

            <div 
              id="main-scroll-container"
              className={`flex-1 flex flex-col h-screen overflow-y-auto overflow-x-hidden transition-all duration-300 ease-in-out ${isSidebarOpen && !isLanding && !isVisitForm ? 'md:ml-72' : 'md:ml-0'} ${isLanding ? 'custom-scrollbar' : ''}`}
            >
              {!isLanding && !isVisitForm && (
                <Header
                  onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
                />
              )}


            <main className={`flex-1 relative z-0 transition-all duration-500 ${isLanding ? 'p-8 md:p-12 lg:p-14' : 'p-6 md:p-10 lg:p-12'}`}>
              <div className="relative z-10">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={location.pathname}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
                  >
                    <Routes location={location} key={location.pathname}>
                      <Route path="/" element={<Navigate to="/quick-actions" replace />} />
                      <Route path="/quick-actions" element={<QuickActions />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/users" element={<Users />} />
                      <Route path="/schedule-visit" element={<ScheduleVisitPage />} />
                      <Route path="/visit-reports" element={<VisitReportsPage />} />
                      <Route path="/visit-report-form" element={<VisitReportForm />} />
                      <Route path="/visit-report-form/:id" element={<VisitReportForm />} />
                      <Route path="/visit-reports/:id/preview" element={<VisitReportPreview />} />
                      <Route path="/audit" element={<AuditPage />} />
                      <Route path="*" element={<Navigate to="/quick-actions" replace />} />
                    </Routes>
                  </motion.div>
                </AnimatePresence>
              </div>
            </main>
          </div>
        </div>
      </ErrorBoundary>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#374151',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '14px',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

// Memoize heavy layout components
const MemoizedSidebar = React.memo(Sidebar);

export default App;
