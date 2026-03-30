import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // PROTECCIÓN DE CIERRE ACCIDENTAL
    const handleBeforeUnload = (e) => {
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
        api.get('/auth/me/').then((resp) => {
          setUser(resp?.data?.user || null);
          // Guardar en almacén unificado
          const merged = { token: access, user: resp?.data?.user || null };
          sessionStorage.setItem('postventa_auth', JSON.stringify(merged));
          setLoading(false);
        }).catch(() => {
          setUser(null);
          setLoading(false);
        });
        return;
      }
    } catch (e) {
      // Si algo falla, continuar como no autenticado
    }
    setUser(null);
    setLoading(false);
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
    } catch (error) {
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
    } catch (error) {
      console.error('Change password error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al cambiar contraseña'
      };
    }
  };

  const value = {
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