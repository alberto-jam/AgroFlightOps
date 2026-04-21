/** TypeScript interfaces for Insumo entity matching Pydantic schemas. */

export interface InsumoResponse {
  id: number;
  nome: string;
  fabricante: string | null;
  unidade_medida: string;
  saldo_atual: number;
  lote: string | null;
  validade: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface InsumoCreate {
  nome: string;
  fabricante?: string | null;
  unidade_medida: string;
  saldo_atual?: number;
  lote?: string | null;
  validade?: string | null;
}

export interface InsumoUpdate {
  nome?: string | null;
  fabricante?: string | null;
  unidade_medida?: string | null;
  saldo_atual?: number | null;
  lote?: string | null;
  validade?: string | null;
}
