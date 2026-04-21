/** TypeScript interfaces for Cultura entity matching Pydantic schemas. */

export interface CulturaResponse {
  id: number;
  nome: string;
  descricao: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface CulturaCreate {
  nome: string;
  descricao?: string | null;
}

export interface CulturaUpdate {
  nome?: string | null;
  descricao?: string | null;
}
