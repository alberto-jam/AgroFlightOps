/** TypeScript interfaces for Propriedade entity matching Pydantic schemas. */

export interface PropriedadeResponse {
  id: number;
  cliente_id: number;
  nome: string;
  endereco: string | null;
  numero: string | null;
  complemento: string | null;
  bairro: string | null;
  municipio: string;
  estado: string;
  cep: string | null;
  localizacao_descritiva: string | null;
  referencia_local: string | null;
  latitude: number | null;
  longitude: number | null;
  area_total: number;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface PropriedadeCreate {
  cliente_id: number;
  nome: string;
  endereco?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  municipio: string;
  estado: string;
  cep?: string | null;
  localizacao_descritiva?: string | null;
  referencia_local?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  area_total: number;
}

export interface PropriedadeUpdate {
  nome?: string | null;
  endereco?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  municipio?: string | null;
  estado?: string | null;
  cep?: string | null;
  localizacao_descritiva?: string | null;
  referencia_local?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  area_total?: number | null;
}
