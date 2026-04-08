import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../services/api';

/**
 * Interface for User data from backend
 */
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'admin' | 'management' | 'technical_service' | 'quality' | 'supervisor' | 'analyst' | 'customer_service' | 'provider';
  is_active: boolean;
  is_staff: boolean;
  last_login?: string;
}

/**
 * Interface for the Auth Context value
 */
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  clearAuth: () => void;
  changePassword: (oldPassword: string, newPassword: string) => Promise<{ success: boolean; error?: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // PROTECCIÓN DE CIERRE ACCIDENTAL
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      // Si el usuario está autenticado, preguntar antes de salir
      const isAuth = sessionStorage.getItem('access_token');
      if (isAuth) {
        e.preventDefault();
        e.returnValue = ''; // Estándar para navegadores modernos
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  useEffect(() => {
    // Restaurar sesión desde sessionStorage (Volátil: muere al cerrar pestaña)
    const restoreSession = async () => {
      try {
        const authDataRaw = sessionStorage.getItem('postventa_auth');
        if (authDataRaw) {
          const authData = JSON.parse(authDataRaw);
          if (authData?.token) {
            api.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`;
            setUser(authData.user || null);
            setLoading(false);
            return;
          }
        }

        const access = sessionStorage.getItem('access_token');
        if (access) {
          api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
          // Intentar cargar perfil actual
          try {
            const resp = await api.get('/auth/me/');
            const userData = resp?.data?.user || null;
            setUser(userData);
            // Guardar en almacén unificado
            const merged = { token: access, user: userData };
            sessionStorage.setItem('postventa_auth', JSON.stringify(merged));
          } catch (err) {
            setUser(null);
          }
          setLoading(false);
          return;
        }
      } catch (e) {
        // Si algo falla, continuar como no autenticado
      }
      setUser(null);
      setLoading(false);
    };

    restoreSession();
  }, []);

  const login = async (username, password) => {
    try {
      setLoading(true);
      const response = await api.post('/auth/login/', {
        username,
        password,
      });

      const { access, refresh, user: userData } = response.data;

      // GUARDAR EN SESSION STORAGE (Volátil)
      sessionStorage.setItem('access_token', access);
      sessionStorage.setItem('refresh_token', refresh);

      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      setUser(userData);
      // Guardar almacén unificado
      sessionStorage.setItem('postventa_auth', JSON.stringify({ token: access, user: userData }));

      return { success: true };
    } catch (error: any) {
      console.error('Login error:', error);

      // Limpiar Volátil
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      sessionStorage.removeItem('postventa_auth');
      // Limpiar Persistente (Posibles variables corrompidas arrastradas)
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('postventa_auth');
      delete api.defaults.headers.common['Authorization'];

      return {
        success: false,
        error: error.response?.data?.detail || error.response?.data?.error || 'Error de autenticación'
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      const refreshToken = sessionStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      sessionStorage.removeItem('postventa_auth');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('postventa_auth');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
    }
  };

  const clearAuth = () => {
    setUser(null);
    setLoading(false);
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('postventa_auth');
    delete api.defaults.headers.common['Authorization'];
  };

  const changePassword = async (oldPassword, newPassword) => {
    try {
      await api.put('/auth/change-password/', {
        old_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: newPassword,
      });
      return { success: true };
    } catch (error: any) {
      console.error('Change password error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al cambiar contraseña'
      };
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    clearAuth,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};