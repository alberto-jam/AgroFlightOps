/** TypeScript interfaces for FinanceiroMissao entity matching Pydantic schemas. */

import type { FinanceiroStatus } from './enums';

export interface FinanceiroMissaoResponse {
  id: number;
  missao_id: number;
  custo_estimado: number;
  custo_realizado: number;
  valor_faturado: number;
  status_financeiro: FinanceiroStatus;
  observacoes: string | null;
  fechado_por: number | null;
  fechado_em: string | null;
  created_at: string;
  updated_at: string;
}

export interface FinanceiroMissaoUpdate {
  custo_estimado?: number | null;
  custo_realizado?: number | null;
  valor_faturado?: number | null;
  status_financeiro?: FinanceiroStatus | null;
  observacoes?: string | null;
}
