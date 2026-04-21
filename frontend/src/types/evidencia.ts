/** TypeScript interfaces for Evidencia entity matching Pydantic schemas. */

export interface EvidenciaResponse {
  id: number;
  missao_id: number;
  nome_arquivo: string;
  url_arquivo: string | null;
  tipo_arquivo: string | null;
  latitude: number | null;
  longitude: number | null;
  enviado_por: number;
  created_at: string;
}

export interface EvidenciaCreate {
  missao_id: number;
  nome_arquivo: string;
  url_arquivo?: string | null;
  tipo_arquivo?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}
