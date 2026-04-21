/** TypeScript interfaces for Drone entity matching Pydantic schemas. */

import type { DroneStatus } from './enums';

export interface DroneResponse {
  id: number;
  identificacao: string;
  modelo: string;
  fabricante: string | null;
  capacidade_litros: number;
  status: DroneStatus;
  horas_voadas: number;
  ultima_manutencao_em: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface DroneCreate {
  identificacao: string;
  modelo: string;
  fabricante?: string | null;
  capacidade_litros: number;
  status?: DroneStatus;
}

export interface DroneUpdate {
  identificacao?: string | null;
  modelo?: string | null;
  fabricante?: string | null;
  capacidade_litros?: number | null;
  status?: DroneStatus | null;
}
