/** TypeScript interfaces for Usuario entity matching Pydantic schemas. */

export interface UsuarioResponse {
  id: number;
  nome: string;
  email: string;
  perfil_id: number;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface UsuarioCreate {
  nome: string;
  email: string;
  perfil_id: number;
  senha: string;
}

export interface UsuarioUpdate {
  nome?: string;
  email?: string;
  perfil_id?: number;
  senha?: string;
}
