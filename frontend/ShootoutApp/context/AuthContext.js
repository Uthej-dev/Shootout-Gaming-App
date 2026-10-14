import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { TOKEN_KEY } from '../constants/config';
import { setAuthToken, setUnauthorizedHandler } from '../services/api';
import * as authService from '../services/authService';
import * as userService from '../services/userService';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY).catch(() => {});
    setAuthToken(null);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    (async () => {
      try {
        const saved = await SecureStore.getItemAsync(TOKEN_KEY);
        if (saved) {
          setAuthToken(saved);
          const me = await userService.me();
          setToken(saved);
          setUser(me);
        }
      } catch {
        await logout();
      } finally {
        setLoading(false);
      }
    })();
  }, [logout]);

  const login = useCallback(async (identifier, password) => {
    const res = await authService.login(identifier, password);
    await SecureStore.setItemAsync(TOKEN_KEY, res.accessToken);
    setAuthToken(res.accessToken);
    setToken(res.accessToken);
    setUser(res.user);
  }, []);

  const register = useCallback((payload) => authService.register(payload), []);

  const value = useMemo(() => ({ user, token, loading, login, logout, register }), [user, token, loading, login, logout, register]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
