/** TypeScript interfaces for ItemChecklistPadrao entity matching Pydantic schemas. */

export interface ItemChecklistPadraoResponse {
  id: number;
  nome_item: string;
  descricao: string | null;
  obrigatorio: boolean;
  ordem_exibicao: number;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface ItemChecklistPadraoCreate {
  nome_item: string;
  descricao?: string | null;
  obrigatorio?: boolean;
  ordem_exibicao?: number;
}

export interface ItemChecklistPadraoUpdate {
  nome_item?: string | null;
  descricao?: string | null;
  obrigatorio?: boolean | null;
  ordem_exibicao?: number | null;
}
