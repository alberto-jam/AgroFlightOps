import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { jwtDecode } from 'jwt-decode';
import apiClient, { TOKEN_KEY } from '../api/client';
import type { AuthState, JwtPayload, LoginResponse, User } from '../types/auth';

export interface AuthContextValue extends AuthState {
  login: (email: string, senha: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

/** Try to restore a user from a stored JWT (if still valid). */
function restoreSession(): { user: User; token: string } | null {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;

  try {
    const payload = jwtDecode<JwtPayload>(token);
    // Reject expired tokens (exp is in seconds)
    if (payload.exp * 1000 < Date.now()) {
      localStorage.removeItem(TOKEN_KEY);
      return null;
    }
    const user: User = {
      id: Number(payload.sub),
      nome: '', // nome is not in the JWT; will be empty until next login
      email: payload.email,
      perfil: payload.perfil,
    };
    return { user, token };
  } catch {
    localStorage.removeItem(TOKEN_KEY);
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  // Restore session on mount
  useEffect(() => {
    const session = restoreSession();
    if (session) {
      setUser(session.user);
      setToken(session.token);
    }
    setReady(true);
  }, []);

  const login = useCallback(async (email: string, senha: string) => {
    const { data } = await apiClient.post<LoginResponse>('/auth/login', {
      email,
      senha,
    });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    setUser(data.usuario);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: !!token && !!user,
      login,
      logout,
    }),
    [user, token, login, logout],
  );

  // Don't render children until we've checked localStorage
  if (!ready) return null;

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
