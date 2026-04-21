/** TypeScript interfaces for MissaoBateria entity matching Pydantic schemas. */

export interface MissaoBateriaResponse {
  id: number;
  missao_id: number;
  bateria_id: number;
  ordem_uso: number;
  created_at: string;
}

export interface MissaoBateriaCreate {
  missao_id: number;
  bateria_id: number;
  ordem_uso: number;
}
