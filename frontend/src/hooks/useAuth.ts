import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api, { API_BASE_URL } from '../services/api';
import { brandConfig } from '../config/brand';
import notificationService from '../services/notificationService';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  last_login?: string;
  permissions?: Record<string, boolean>;
  accessible_pages?: string[];
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

const AUTH_STORAGE_KEY = 'postventa_auth';

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
  });
  const [isLoading, setIsLoading] = useState(true);

  // Reemplazo de QueryClient para evitar errores de contexto
  const queryClient = { clear: () => {} };

  // Restore session
  useEffect(() => {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      try {
        const { user, token } = JSON.parse(stored);
        setAuthState({ user, token, isAuthenticated: true });
      } catch (e) {
        localStorage.removeItem(AUTH_STORAGE_KEY);
      }
    }
    setIsLoading(false);
  }, []);

  const saveAuthState = useCallback((user: User, token: string) => {
    const authData = { user, token };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));
    setAuthState({ user, token, isAuthenticated: true });
  }, []);

  const clearAuthState = useCallback(() => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem('refresh_token');
    setAuthState({ user: null, token: null, isAuthenticated: false });
  }, []);

  // Login simplificado sin useMutation
  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      const response = await api.post('auth/login/', credentials);
      const data = response.data;
      
      let detectedCountry = 'CL';
      const lowerUsername = data.user.username.toLowerCase();
      if (lowerUsername.endsWith('.pe')) detectedCountry = 'PE';
      else if (lowerUsername.endsWith('.co')) detectedCountry = 'CO';
      
      localStorage.setItem('country_code', detectedCountry);
      saveAuthState(data.user, data.access);
      if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
      
      try { notificationService.connect(); } catch (e) {}
      toast.success(`¡Bienvenido, ${data.user.username}!`);
      
      // IMMEDIATE REDIRECT: Avoid flickering or intermediate pages
      window.location.href = '/quick-actions';
    } catch (error: any) {
      toast.error(error.message || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try { await api.post('auth/logout/', { refresh_token: refreshToken }); } catch (e) {}
    }
    clearAuthState();
    localStorage.removeItem('country_code');
    toast.success('Sesión cerrada');
    setTimeout(() => window.location.reload(), 500);
  };

  const getUserDisplayName = useCallback((): string => {
    if (!authState.user) return '';
    return authState.user.first_name ? `${authState.user.first_name} ${authState.user.last_name}` : authState.user.username;
  }, [authState.user]);

  const hasPermission = (p: string) => true; // Bypass temporal
  const hasRole = (r: string) => true; // Bypass temporal

  return {
    user: authState.user,
    token: authState.token,
    isAuthenticated: authState.isAuthenticated,
    isLoading,
    login,
    logout,
    hasPermission,
    hasRole,
    getUserDisplayName,
  };
}
