/** TypeScript interfaces for TipoOcorrencia entity matching Pydantic schemas. */

export interface TipoOcorrenciaResponse {
  id: number;
  nome: string;
  descricao: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface TipoOcorrenciaCreate {
  nome: string;
  descricao?: string | null;
}

export interface TipoOcorrenciaUpdate {
  nome?: string | null;
  descricao?: string | null;
}
