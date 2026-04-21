/** TypeScript interfaces for ReservaInsumo and ConsumoInsumoMissao matching Pydantic schemas. */

export interface ReservaInsumoResponse {
  id: number;
  missao_id: number;
  insumo_id: number;
  quantidade_prevista: number;
  unidade_medida: string;
  justificativa_excesso: string | null;
  created_at: string;
}

export interface ReservaInsumoCreate {
  missao_id: number;
  insumo_id: number;
  quantidade_prevista: number;
  unidade_medida: string;
  justificativa_excesso?: string | null;
}

export interface ConsumoInsumoMissaoResponse {
  id: number;
  missao_id: number;
  insumo_id: number;
  quantidade_realizada: number;
  unidade_medida: string;
  observacoes: string | null;
  justificativa_excesso: string | null;
  created_at: string;
}

export interface ConsumoInsumoMissaoCreate {
  missao_id: number;
  insumo_id: number;
  quantidade_realizada: number;
  unidade_medida: string;
  observacoes?: string | null;
  justificativa_excesso?: string | null;
}
