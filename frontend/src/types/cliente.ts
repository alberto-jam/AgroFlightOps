/** TypeScript interfaces for Cliente entity matching Pydantic schemas. */

export interface ClienteResponse {
  id: number;
  nome: string;
  cpf_cnpj: string | null;
  telefone: string | null;
  email: string | null;
  endereco: string | null;
  numero: string | null;
  complemento: string | null;
  bairro: string | null;
  municipio: string | null;
  estado: string | null;
  cep: string | null;
  latitude: number | null;
  longitude: number | null;
  referencia_local: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClienteCreate {
  nome: string;
  cpf_cnpj?: string | null;
  telefone?: string | null;
  email?: string | null;
  endereco?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  municipio?: string | null;
  estado?: string | null;
  cep?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  referencia_local?: string | null;
}

export interface ClienteUpdate {
  nome?: string | null;
  cpf_cnpj?: string | null;
  telefone?: string | null;
  email?: string | null;
  endereco?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  municipio?: string | null;
  estado?: string | null;
  cep?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  referencia_local?: string | null;
}
