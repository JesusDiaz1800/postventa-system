import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api, { API_BASE_URL } from '../services/api';
<<<<<<< HEAD
=======
import { brandConfig } from '../config/brand';
import notificationService from '../services/notificationService';
>>>>>>> 674c244 (tus cambios)

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

  // Load auth state from localStorage on mount
  useEffect(() => {
    const loadAuthState = () => {
      try {
        // Verificar si es la primera vez que se carga la app
        const hasBeenInitialized = sessionStorage.getItem('app_initialized');
        
        if (!hasBeenInitialized) {
          // Primera carga - forzar logout
          localStorage.removeItem(AUTH_STORAGE_KEY);
          localStorage.removeItem('refresh_token');
          sessionStorage.setItem('app_initialized', 'true');
          setAuthState({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        } else {
          // Cargas posteriores - mantener sesión si existe
          const stored = localStorage.getItem(AUTH_STORAGE_KEY);
          if (stored) {
            const { user, token } = JSON.parse(stored);
            if (user && token) {
              setAuthState({
                user,
                token,
                isAuthenticated: true,
              });
            }
          }
        }
      } catch (error) {
        console.warn('Error loading auth state:', error);
        localStorage.removeItem(AUTH_STORAGE_KEY);
      } finally {
        setIsLoading(false);
      }
    };

    loadAuthState();
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

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginCredentials): Promise<AuthResponse> => {
<<<<<<< HEAD
      const response = await api.post('/auth/login/', credentials);
=======
      const response = await api.post('auth/login/', credentials);
>>>>>>> 674c244 (tus cambios)
      return response.data;
    },
    onSuccess: (data) => {
      saveAuthState(data.user, data.access);
      // Guardar refresh token si está disponible
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
      }
<<<<<<< HEAD
=======
      
      // Reconectar WebSocket después del login
      try {
        notificationService.connect();
        console.log('🔌 WebSocket reconectado después del login');
      } catch (error) {
        console.warn('⚠️ Error reconectando WebSocket:', error);
      }
      
>>>>>>> 674c244 (tus cambios)
      toast.success(`¡Bienvenido, ${data.user.username}!`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al iniciar sesión');
    },
  });

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: async () => {
<<<<<<< HEAD
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          await api.post('/auth/logout/', { refresh: refreshToken });
        } catch (error) {
          console.warn('Error during logout request:', error);
=======
      console.log('🔄 Ejecutando logoutMutation');
      
      // Desconectar WebSocket
      try {
        notificationService.disconnect();
        console.log('🔌 WebSocket desconectado');
      } catch (error) {
        console.warn('⚠️ Error desconectando WebSocket:', error);
      }
      
      const refreshToken = localStorage.getItem('refresh_token');
      console.log('Refresh token encontrado:', refreshToken ? 'Sí' : 'No');
      if (refreshToken) {
        try {
          console.log('📤 Enviando request de logout...');
          await api.post('auth/logout/', { refresh_token: refreshToken });
          console.log('✅ Request de logout exitosa');
        } catch (error) {
          console.warn('❌ Error during logout request:', error);
>>>>>>> 674c244 (tus cambios)
        }
      }
    },
    onSuccess: () => {
<<<<<<< HEAD
      clearAuthState();
      toast.success('Sesión cerrada correctamente');
    },
    onError: () => {
      clearAuthState();
      toast.success('Sesión cerrada correctamente');
=======
      console.log('✅ Logout mutation exitosa');
      clearAuthState();
      // Limpiar sessionStorage también
      sessionStorage.removeItem('app_initialized');
      toast.success('Sesión cerrada correctamente');
      // Forzar recarga de página para limpiar todo el estado
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    },
    onError: (error) => {
      console.log('❌ Error en logout mutation:', error);
      clearAuthState();
      // Limpiar sessionStorage también
      sessionStorage.removeItem('app_initialized');
      toast.success('Sesión cerrada correctamente');
      // Forzar recarga de página para limpiar todo el estado
      setTimeout(() => {
        window.location.reload();
      }, 1000);
>>>>>>> 674c244 (tus cambios)
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
<<<<<<< HEAD
=======
    console.log('🔄 Función logout llamada desde useAuth');
>>>>>>> 674c244 (tus cambios)
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
