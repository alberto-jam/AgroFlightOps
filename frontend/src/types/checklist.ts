/** TypeScript interfaces for Checklist entities matching Pydantic schemas. */

import type { ChecklistStatusGeral, ItemChecklistStatus } from './enums';

export interface ItemChecklistMissaoResponse {
  id: number;
  checklist_id: number;
  nome_item: string;
  obrigatorio: boolean;
  status_item: ItemChecklistStatus;
  observacao: string | null;
  created_at: string;
  updated_at: string;
}

export interface ItemChecklistMissaoUpdate {
  status_item: ItemChecklistStatus;
  observacao?: string | null;
}

export interface ChecklistMissaoResponse {
  id: number;
  missao_id: number;
  status_geral: ChecklistStatusGeral;
  preenchido_por: number;
  revisado_por: number | null;
  preenchido_em: string;
  revisado_em: string | null;
  observacoes: string | null;
  itens: ItemChecklistMissaoResponse[];
  created_at: string;
  updated_at: string;
}
