/** TypeScript interfaces for Manutencao entity matching Pydantic schemas. */

export interface ManutencaoResponse {
  id: number;
  drone_id: number;
  tipo: string;
  descricao: string | null;
  data_manutencao: string;
  proxima_manutencao: string | null;
  horas_na_data: number | null;
  created_at: string;
  updated_at: string;
}

export interface ManutencaoCreate {
  drone_id: number;
  tipo: string;
  descricao?: string | null;
  data_manutencao: string;
  proxima_manutencao?: string | null;
  horas_na_data?: number | null;
}

export interface ManutencaoUpdate {
  tipo?: string | null;
  descricao?: string | null;
  data_manutencao?: string | null;
  proxima_manutencao?: string | null;
  horas_na_data?: number | null;
}
