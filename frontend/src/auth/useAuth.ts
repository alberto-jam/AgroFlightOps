import { useContext } from 'react';
import { AuthContext, type AuthContextValue } from './AuthContext';

/**
 * Convenience hook that consumes the AuthContext.
 * Throws if used outside an AuthProvider.
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an <AuthProvider>');
  }
  return ctx;
}
