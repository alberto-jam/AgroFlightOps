/** TypeScript interfaces for Bateria entity matching Pydantic schemas. */

import type { BateriaStatus } from './enums';

export interface BateriaResponse {
  id: number;
  identificacao: string;
  drone_id: number | null;
  status: BateriaStatus;
  observacoes: string | null;
  ciclos: number;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface BateriaCreate {
  identificacao: string;
  drone_id?: number | null;
  status?: BateriaStatus;
  observacoes?: string | null;
}

export interface BateriaUpdate {
  identificacao?: string | null;
  drone_id?: number | null;
  status?: BateriaStatus | null;
  observacoes?: string | null;
}
