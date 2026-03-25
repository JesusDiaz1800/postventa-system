import { useEffect, useState, lazy, Suspense } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// PWA Components (keep eager - needed immediately)
import PWAInstaller from './components/PWAInstaller';
import PWAUpdate from './components/PWAUpdate';
// OfflineIndicator removed
import { PWAProvider } from './context/PWAContext'; // Import Provider

// Core Components (keep eager - needed for layout)
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Sidebar';
import Login from './pages/Login';
import { LoadingSpinner } from './components/LoadingSpinner';
import { Logo } from './components/Logo';
import { ErrorBoundary } from './components/ErrorBoundary';

// Lazy load global utilities
const FloatingAIChat = lazy(() => import('./components/FloatingAIChat').then(module => ({ default: module.FloatingAIChat })));
const GlobalSearch = lazy(() => import('./components/GlobalSearch').then(module => ({ default: module.GlobalSearch })));

// Lazy load all pages for code-splitting

const Incidents = lazy(() => import('./pages/IncidentsControl.jsx'));
const CreateIncident = lazy(() => import('./pages/CreateIncident.jsx'));
const AIPage = lazy(() => import('./pages/AIPage'));
const AuditPage = lazy(() => import('./pages/AuditPage'));
const ReportsPage = lazy(() => import('./pages/ReportsPage'));
const Users = lazy(() => import('./pages/Users'));
const VisitReportsPage = lazy(() => import('./pages/VisitReportsPage'));
const ClientQualityReportsPage = lazy(() => import('./pages/ClientQualityReportsPage'));
const InternalQualityReportsPage = lazy(() => import('./pages/InternalQualityReportsPage'));
const SupplierReportsPage = lazy(() => import('./pages/SupplierReportsPage'));
const Documents = lazy(() => import('./pages/Documents'));
const VisitReportForm = lazy(() => import('./pages/VisitReportForm'));
const QualityReportForm = lazy(() => import('./pages/QualityReportForm'));
const SupplierReportForm = lazy(() => import('./pages/SupplierReportForm'));

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
    document.title = "Postventa v1.0 - REFRESHED";
  }, []);

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

  const isDashboard = location.pathname === '/reports';
  const isAI = location.pathname.startsWith('/ai');

  return (
    <PWAProvider>
      <div className={`min-h-screen relative transition-colors duration-500 ${isDashboard ? 'bg-[#030014] text-white' : 'bg-slate-50/30 text-slate-900'}`}>
        {/* Capas de Fondo Premium - Condicionales */}
        {isDashboard ? (
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
            <Suspense fallback={null}>
              <GlobalSearch />
            </Suspense>
            <Sidebar
              currentPath={location.pathname}
              onNavigate={(path) => navigate(path)}
              userName={getUserDisplayName()}
              userRole={user.role}
              isOpen={isSidebarOpen}
              onClose={() => setIsSidebarOpen(false)}
            />

            <div 
              id="main-scroll-container"
              className={`flex-1 flex flex-col h-screen overflow-y-auto overflow-x-hidden transition-all duration-300 ease-in-out ${isSidebarOpen ? 'md:ml-72' : 'md:ml-0'} ${isDashboard ? 'custom-scrollbar' : ''}`}
            >
              <Header
                onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
              />

              <main className={`flex-1 relative z-0 transition-all duration-500 ${isAI ? 'p-0' : (isDashboard ? 'p-8 md:p-12 lg:p-14' : 'p-6 md:p-10 lg:p-12')}`}>
                <div className={`relative z-10 ${isAI ? 'h-full' : ''}`}>
                  <Suspense fallback={<PageLoader />}>
                    <Routes>
                      <Route path="/" element={<Navigate to="/reports" replace />} />
                      <Route path="/incidents" element={<Incidents />} />
                      <Route path="/incidents/new" element={<CreateIncident />} />
                      <Route path="/incidents/:id/edit" element={<CreateIncident />} />
                      <Route path="/incidents/:id" element={<Incidents />} />
                      <Route path="/reports" element={<ReportsPage />} />
                      <Route path="/users" element={<Users />} />
                      <Route path="/visit-reports" element={<VisitReportsPage />} />
                      <Route path="/quality-reports/client" element={<ClientQualityReportsPage />} />
                      <Route path="/quality-reports/internal" element={<InternalQualityReportsPage />} />
                      <Route path="/supplier-reports" element={<SupplierReportsPage />} />
                      <Route path="/documents" element={<Documents />} />
                      <Route path="/visit-report-form" element={<VisitReportForm />} />
                      <Route path="/visit-report-form/:id" element={<VisitReportForm />} />
                      <Route path="/quality-report-form/:incidentId" element={<QualityReportForm />} />
                      <Route path="/supplier-report-form/:incidentId" element={<SupplierReportForm />} />
                      <Route path="/supplier-report-form" element={<SupplierReportForm />} />
                      <Route path="/ai" element={<AIPage />} />
                      <Route path="/audit" element={<AuditPage />} />
                      <Route path="*" element={<Navigate to="/reports" replace />} />
                    </Routes>
                  </Suspense>
                </div>
              </main>
            </div>
          </div>
        </ErrorBoundary>

        <Suspense fallback={null}>
          <FloatingAIChat />
        </Suspense>

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

        <PWAInstaller />
        <PWAUpdate />

      </div>
    </PWAProvider>
  );
}

export default App;
