/** TypeScript interfaces for Perfil entity matching Pydantic schemas. */

export interface PerfilResponse {
  id: number;
  nome: string;
  descricao: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface PerfilCreate {
  nome: string;
  descricao?: string | null;
}

export interface PerfilUpdate {
  nome?: string | null;
  descricao?: string | null;
}
