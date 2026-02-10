import { useEffect, useState, lazy, Suspense } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// PWA Components (keep eager - needed immediately)
import PWAInstaller from './components/PWAInstaller';
import PWAUpdate from './components/PWAUpdate';
import OfflineIndicator from './components/OfflineIndicator';
import { PWAProvider } from './context/PWAContext'; // Import Provider

// Core Components (keep eager - needed for layout)
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Sidebar';
import { LoginIndustrial } from './components/LoginIndustrial';
import { LoadingSpinner } from './components/LoadingSpinner';
import { Logo } from './components/Logo';
import { ErrorBoundary } from './components/ErrorBoundary';
import { FloatingAIChat } from './components/FloatingAIChat';

// Lazy load all pages for code-splitting

const Incidents = lazy(() => import('./pages/Incidents.jsx'));
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
const Settings = lazy(() => import('./pages/Settings'));
const VisitReportForm = lazy(() => import('./pages/VisitReportForm'));
const QualityReportForm = lazy(() => import('./pages/QualityReportForm'));
const SupplierReportForm = lazy(() => import('./pages/SupplierReportForm'));

// Hooks
import { useAuth } from './hooks/useAuth';
import { useTheme } from './hooks/useTheme';

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
  const { theme } = useTheme();
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => window.innerWidth >= 1024);
  const navigate = useNavigate();
  const location = useLocation();
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
    document.title = brandConfig.app.title;
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
    return (
      <ErrorBoundary>
        <LoginIndustrial onSubmit={login} isLoading={isLoading} />
      </ErrorBoundary>
    );
  }

  return (
    <PWAProvider>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <ErrorBoundary>
          <div className="flex">
            <Sidebar
              currentPath={location.pathname}
              onNavigate={(path) => navigate(path)}
              userName={getUserDisplayName()}
              userRole={user.role}
              isOpen={isSidebarOpen}
              onClose={() => setIsSidebarOpen(false)}
            />

            <div className={`flex-1 flex flex-col h-screen overflow-y-auto overflow-x-hidden transition-all duration-300 ease-in-out bg-gray-50 ${isSidebarOpen ? 'md:ml-72' : 'md:ml-0'}`}>
              <Header
                onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
              />

              <main className="flex-1 bg-transparent p-4 md:p-6 lg:p-8 relative z-0">
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
                    <Route path="/quality-report-form/:incidentId" element={<QualityReportForm />} />
                    <Route path="/supplier-report-form/:incidentId" element={<SupplierReportForm />} />
                    <Route path="/supplier-report-form" element={<SupplierReportForm />} />
                    <Route path="/ai" element={<AIPage />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/audit" element={<AuditPage />} />
                    <Route path="*" element={<Navigate to="/reports" replace />} />
                  </Routes>
                </Suspense>
              </main>
            </div>
          </div>
        </ErrorBoundary>

        <FloatingAIChat />

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
        <OfflineIndicator />
      </div>
    </PWAProvider>
  );
}

export default App;
