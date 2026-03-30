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

  const queryClient = useQueryClient();

  // NO auto-restaurar sesión desde localStorage
  // El usuario debe hacer login explícitamente cada vez
  useEffect(() => {
    setIsLoading(false);
  }, []);

  // Save auth state to localStorage
  const saveAuthState = useCallback((user: User, token: string) => {
    const authData = { user, token };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));
    setAuthState({
      user,
      token,
      isAuthenticated: true,
    });
  }, []);

  // Clear auth state
  const clearAuthState = useCallback(() => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem('refresh_token');
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
    queryClient.clear();
  }, [queryClient]);

  // Handle auth:logout event from api interceptor
  useEffect(() => {
    const handleLogout = () => {
      clearAuthState();
      toast.error('Tu sesión ha expirado');
    };

    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, [clearAuthState]);

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginCredentials): Promise<AuthResponse> => {
      const response = await api.post('auth/login/', credentials);
      return response.data;
    },
    onSuccess: (data) => {
      // Detección Automática de País basada en el usuario
      let detectedCountry = 'CL'; // Default Chile
      const lowerUsername = data.user.username.toLowerCase();

      if (lowerUsername.endsWith('.pe')) {
        detectedCountry = 'PE';
      } else if (lowerUsername.endsWith('.co')) {
        detectedCountry = 'CO';
      }

      // Forzar actualización inmediata del país
      localStorage.setItem('country_code', detectedCountry);

      saveAuthState(data.user, data.access);
      // Guardar refresh token si está disponible
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
      }

      // Reconectar WebSocket después del login
      try {
        notificationService.connect();
      } catch (error) {
        // Silent fail for WebSocket
      }

      toast.success(`¡Bienvenido, ${data.user.username}!`);

      // Pequeño delay para asegurar que el header se actualice en api.js antes de siguientes peticiones
      // Opcional: forzar recarga si el país cambió drásticamente, pero api.js lee localStorage encada request
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al iniciar sesión');
    },
  });

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: async () => {
      // Desconectar WebSocket
      try {
        notificationService.disconnect();
      } catch (error) {
        // Silent fail
      }

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          await api.post('auth/logout/', { refresh_token: refreshToken });
        } catch (error) {
          // Silent fail
        }
      }
    },
    onSuccess: () => {
      clearAuthState();
      // Limpiar sessionStorage también
      sessionStorage.removeItem('app_initialized');
      // LIMPIEZA CRÍTICA: Borrar país para no afectar próxima sesión
      localStorage.removeItem('country_code');

      toast.success('Sesión cerrada correctamente');
      // Forzar recarga de página para limpiar todo el estado
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    },
    onError: (error) => {
      clearAuthState();
      // Limpiar sessionStorage también
      sessionStorage.removeItem('app_initialized');
      toast.success('Sesión cerrada correctamente');
      // Forzar recarga de página para limpiar todo el estado
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    },
  });

  // Refresh token mutation
  const refreshMutation = useMutation({
    mutationFn: async (): Promise<{ access: string }> => {
      const stored = localStorage.getItem(AUTH_STORAGE_KEY);
      if (!stored) throw new Error('No refresh token available');

      const { token } = JSON.parse(stored);
      const response = await api.post('/auth/token/refresh/', { refresh: token });
      return response.data;
    },
    onSuccess: (data) => {
      if (authState.user) {
        saveAuthState(authState.user, data.access);
      }
    },
    onError: () => {
      clearAuthState();
    },
  });

  // User profile query
  const userQuery = useQuery({
    queryKey: ['user', authState.user?.id],
    queryFn: async (): Promise<User> => {
      if (!authState.token) throw new Error('No token available');
      const response = await api.get('/users/me/');
      return response.data;
    },
    enabled: authState.isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Login function
  const login = useCallback((credentials: LoginCredentials) => {
    loginMutation.mutate(credentials);
  }, [loginMutation]);

  // Logout function
  const logout = useCallback(() => {
    logoutMutation.mutate();
  }, [logoutMutation]);

  // Refresh token function
  const refreshToken = useCallback(() => {
    refreshMutation.mutate();
  }, [refreshMutation]);

  // Check if user has permission
  const hasPermission = useCallback((permission: string): boolean => {
    if (!authState.user) return false;

    const roleConfig = brandConfig.roles[authState.user.role as keyof typeof brandConfig.roles];
    if (!roleConfig) return false;

    return roleConfig.permissions.includes('all') || roleConfig.permissions.includes(permission);
  }, [authState.user]);

  // Check if user has role
  const hasRole = useCallback((role: string): boolean => {
    return authState.user?.role === role;
  }, [authState.user]);

  // Get user display name
  const getUserDisplayName = useCallback((): string => {
    if (!authState.user) return '';

    if (authState.user.first_name && authState.user.last_name) {
      return `${authState.user.first_name} ${authState.user.last_name}`;
    }

    return authState.user.username;
  }, [authState.user]);

  // Get role display name
  const getRoleDisplayName = useCallback((): string => {
    if (!authState.user) return '';

    const roleConfig = brandConfig.roles[authState.user.role as keyof typeof brandConfig.roles];
    return roleConfig?.name || authState.user.role;
  }, [authState.user]);

  return {
    // State
    user: authState.user,
    token: authState.token,
    isAuthenticated: authState.isAuthenticated,
    isLoading: isLoading || loginMutation.isPending || logoutMutation.isPending,

    // Actions
    login,
    logout,
    refreshToken,

    // Utilities
    hasPermission,
    hasRole,
    getUserDisplayName,
    getRoleDisplayName,

    // Queries
    userQuery,

    // Mutations
    loginMutation,
    logoutMutation,
    refreshMutation,
  };
}
