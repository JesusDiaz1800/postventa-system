import { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';

// PWA Components
import PWAInstaller from './components/PWAInstaller';
import PWAUpdate from './components/PWAUpdate';
import OfflineIndicator from './components/OfflineIndicator';

// Components
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { LoginForm } from './components/LoginForm';
import { Dashboard } from './components/Dashboard';
import Incidents from './pages/Incidents.jsx';
import CreateIncident from './pages/CreateIncident.jsx';
// Imports moved to active imports above
import AIPage from './pages/AIPage';
import WorkflowsPage from './pages/WorkflowsPage';
import AuditPage from './pages/AuditPage';
import ReportsPage from './pages/ReportsPage';
import Users from './pages/Users';
import VisitReportsPage from './pages/VisitReportsPage';
import ClientQualityReportsPage from './pages/ClientQualityReportsPage';
import InternalQualityReportsPage from './pages/InternalQualityReportsPage';
import SupplierReportsPage from './pages/SupplierReportsPage';
import LabReportsPage from './pages/LabReportsPage';
import Documents from './pages/Documents';
import Settings from './pages/Settings';
// Formularios específicos
import VisitReportForm from './pages/VisitReportForm';
import QualityReportForm from './pages/QualityReportForm';
import SupplierReportForm from './pages/SupplierReportForm';
import LabReportForm from './pages/LabReportForm';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorBoundary } from './components/ErrorBoundary';

// Hooks
import { useAuth } from './hooks/useAuth';
import { useTheme } from './hooks/useTheme';

// Utils
import { brandConfig } from './config/brand';


function App() {
  const { user, isLoading, login, logout } = useAuth();
  const { theme } = useTheme();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  // Set document title
  useEffect(() => {
    document.title = brandConfig.app.title;
  }, []);

  // Set theme
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return (
      <ErrorBoundary>
        <LoginForm onSubmit={login} />
      </ErrorBoundary>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-100 app-container">
          <ErrorBoundary>
            <div className="flex">
              <Sidebar 
                currentPath={location.pathname}
                onNavigate={(path) => navigate(path)}
                userRole={user.role}
                isOpen={isSidebarOpen}
              />
              
              <div className={`flex-1 transition-all duration-300 ease-in-out main-content ${
                isSidebarOpen ? 'md:ml-64' : 'md:ml-0'
              }`}>
                <Header 
                  user={user} 
                  onLogout={logout}
                  currentPage={location.pathname}
                  onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
                  isSidebarOpen={isSidebarOpen}
                />
                
                <main className="bg-transparent">
                  <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-6">
                <Routes>
                  <Route path="/" element={<Navigate to="/reports" replace />} />
                  <Route path="/dashboard" element={<Dashboard stats={{
                    totalIncidents: 0,
                    pendingIncidents: 0,
                    resolvedIncidents: 0,
                    averageResolutionTime: 0,
                    aiAnalyses: 0,
                    activeUsers: 0
                  }} recentIncidents={[]} />} />
                  <Route path="/incidents" element={<Incidents />} />
                  <Route path="/incidents/new" element={<CreateIncident />} />
                  <Route path="/incidents/:id" element={<Incidents />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/users" element={<Users />} />
                  <Route path="/visit-reports" element={<VisitReportsPage />} />
                  <Route path="/quality-reports/client" element={<ClientQualityReportsPage />} />
                  <Route path="/quality-reports/internal" element={<InternalQualityReportsPage />} />
                  <Route path="/supplier-reports" element={<SupplierReportsPage />} />
                  <Route path="/lab-reports" element={<LabReportsPage />} />
                  <Route path="/documents" element={<Documents />} />
                  {/* Formularios específicos */}
                  <Route path="/visit-report-form" element={<VisitReportForm />} />
                  <Route path="/quality-report-form/:incidentId" element={<QualityReportForm />} />
                  <Route path="/supplier-report-form/:incidentId" element={<SupplierReportForm />} />
                  <Route path="/lab-report-form" element={<LabReportForm />} />
                  <Route path="/ai" element={<AIPage />} />
                  <Route path="/workflows" element={<WorkflowsPage />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/audit" element={<AuditPage />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
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
                borderRadius: '0.5rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
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
      {/* ReactQueryDevtools oculto */}
      {/* {(import.meta as any).env?.DEV && (
        <ReactQueryDevtools initialIsOpen={false} />
      )} */}
      
      {/* PWA Components */}
      <PWAInstaller />
      <PWAUpdate />
      <OfflineIndicator />
    </div>
  );
}

export default App;
