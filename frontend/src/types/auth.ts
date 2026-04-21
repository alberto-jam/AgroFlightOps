/** Authentication-related TypeScript interfaces. */

export type Perfil =
  | 'ADMINISTRADOR'
  | 'COORDENADOR_OPERACIONAL'
  | 'PILOTO'
  | 'TECNICO'
  | 'FINANCEIRO';

export interface User {
  id: number;
  nome: string;
  email: string;
  perfil: Perfil;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface LoginRequest {
  email: string;
  senha: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: User;
}

/** JWT payload shape (decoded from access_token). */
export interface JwtPayload {
  sub: string;       // usuario_id
  perfil: Perfil;
  email: string;
  exp: number;
  iat: number;
}
