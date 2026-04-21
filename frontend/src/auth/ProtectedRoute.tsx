import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './useAuth';
import type { Perfil } from '../types/auth';

interface ProtectedRouteProps {
  /** If provided, only these profiles may access the route. */
  allowedPerfis?: Perfil[];
}

/**
 * Route guard.
 * - Redirects to /login when not authenticated.
 * - Shows a 403-style redirect when the user's profile is not allowed.
 */
export function ProtectedRoute({ allowedPerfis }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedPerfis && user && !allowedPerfis.includes(user.perfil)) {
    // Redirect to dashboard with a "forbidden" flag the dashboard can display
    return <Navigate to="/dashboard?forbidden=1" replace />;
  }

  return <Outlet />;
}
