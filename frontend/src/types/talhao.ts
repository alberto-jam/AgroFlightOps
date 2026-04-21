/** TypeScript interfaces for Talhao entity matching Pydantic schemas. */

export interface TalhaoResponse {
  id: number;
  propriedade_id: number;
  nome: string;
  area_hectares: number;
  cultura_id: number;
  observacoes: string | null;
  latitude: number | null;
  longitude: number | null;
  ponto_referencia: string | null;
  geojson: Record<string, unknown> | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface TalhaoCreate {
  propriedade_id: number;
  nome: string;
  area_hectares: number;
  cultura_id: number;
  observacoes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  ponto_referencia?: string | null;
  geojson?: Record<string, unknown> | null;
}

export interface TalhaoUpdate {
  nome?: string | null;
  area_hectares?: number | null;
  cultura_id?: number | null;
  observacoes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  ponto_referencia?: string | null;
  geojson?: Record<string, unknown> | null;
}
