/** TypeScript interfaces for Missao entity matching Pydantic schemas. */

import type { MissaoStatus } from './enums';

export interface MissaoResponse {
  id: number;
  codigo: string;
  ordem_servico_id: number;
  piloto_id: number;
  tecnico_id: number | null;
  drone_id: number;
  data_agendada: string;
  hora_agendada: string;
  area_prevista: number;
  area_realizada: number | null;
  volume_previsto: number;
  volume_realizado: number | null;
  janela_operacional: string | null;
  restricoes: string | null;
  observacoes_planejamento: string | null;
  observacoes_execucao: string | null;
  status: MissaoStatus;
  latitude_operacao: number | null;
  longitude_operacao: number | null;
  endereco_operacao: string | null;
  referencia_operacao: string | null;
  iniciado_em: string | null;
  finalizado_em: string | null;
  encerrado_tecnicamente_em: string | null;
  encerrado_financeiramente_em: string | null;
  created_at: string;
  updated_at: string;
}

export interface MissaoCreate {
  ordem_servico_id: number;
  piloto_id: number;
  tecnico_id?: number | null;
  drone_id: number;
  data_agendada: string;
  hora_agendada: string;
  area_prevista: number;
  volume_previsto: number;
  janela_operacional?: string | null;
  restricoes?: string | null;
  observacoes_planejamento?: string | null;
  latitude_operacao?: number | null;
  longitude_operacao?: number | null;
  endereco_operacao?: string | null;
  referencia_operacao?: string | null;
}

export interface MissaoUpdate {
  piloto_id?: number | null;
  tecnico_id?: number | null;
  drone_id?: number | null;
  data_agendada?: string | null;
  hora_agendada?: string | null;
  area_prevista?: number | null;
  area_realizada?: number | null;
  volume_previsto?: number | null;
  volume_realizado?: number | null;
  janela_operacional?: string | null;
  restricoes?: string | null;
  observacoes_planejamento?: string | null;
  observacoes_execucao?: string | null;
  latitude_operacao?: number | null;
  longitude_operacao?: number | null;
  endereco_operacao?: string | null;
  referencia_operacao?: string | null;
}

export interface MissaoRegistroExecucao {
  area_realizada?: number | null;
  volume_realizado?: number | null;
  observacoes_execucao?: string | null;
}

export interface MissaoTransicao {
  status_novo: MissaoStatus;
  motivo?: string | null;
}

export interface HistoricoStatusMissaoResponse {
  id: number;
  missao_id: number;
  status_anterior: string | null;
  status_novo: string;
  motivo: string | null;
  alterado_por: number;
  created_at: string;
}
