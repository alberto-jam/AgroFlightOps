/** TypeScript interfaces for OrdemServico entity matching Pydantic schemas. */

import type { OrdemServicoStatus, Prioridade } from './enums';

export interface OrdemServicoResponse {
  id: number;
  codigo: string;
  cliente_id: number;
  propriedade_id: number;
  talhao_id: number;
  cultura_id: number;
  tipo_aplicacao: string;
  prioridade: Prioridade;
  descricao: string | null;
  data_prevista: string;
  status: OrdemServicoStatus;
  motivo_rejeicao: string | null;
  motivo_cancelamento: string | null;
  criado_por: number;
  aprovado_por: number | null;
  created_at: string;
  updated_at: string;
}

export interface OrdemServicoCreate {
  cliente_id: number;
  propriedade_id: number;
  talhao_id: number;
  cultura_id: number;
  tipo_aplicacao: string;
  prioridade: Prioridade;
  descricao?: string | null;
  data_prevista: string;
}

export interface OrdemServicoUpdate {
  tipo_aplicacao?: string | null;
  prioridade?: Prioridade | null;
  descricao?: string | null;
  data_prevista?: string | null;
}

export interface OrdemServicoTransicao {
  status_novo: OrdemServicoStatus;
  motivo?: string | null;
}

export interface HistoricoStatusOSResponse {
  id: number;
  ordem_servico_id: number;
  status_anterior: string | null;
  status_novo: string;
  motivo: string | null;
  alterado_por: number;
  created_at: string;
}
