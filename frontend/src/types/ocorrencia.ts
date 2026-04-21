/** TypeScript interfaces for Ocorrencia entity matching Pydantic schemas. */

import type { Severidade } from './enums';

export interface OcorrenciaResponse {
  id: number;
  missao_id: number;
  tipo_ocorrencia_id: number;
  descricao: string;
  severidade: Severidade;
  registrada_por: number;
  registrada_em: string;
  created_at: string;
  updated_at: string;
}

export interface OcorrenciaCreate {
  missao_id: number;
  tipo_ocorrencia_id: number;
  descricao: string;
  severidade: Severidade;
}
