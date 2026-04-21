/** TypeScript interfaces for DocumentoOficial entity matching Pydantic schemas. */

import type { DocumentoEntidade, DocumentoStatus } from './enums';

export interface DocumentoOficialResponse {
  id: number;
  entidade: DocumentoEntidade;
  entidade_id: number;
  tipo_documento: string;
  descricao: string | null;
  nome_arquivo: string;
  content_type: string;
  s3_key: string;
  bucket_s3: string | null;
  data_emissao: string | null;
  data_validade: string | null;
  status: DocumentoStatus;
  enviado_por: number | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentoOficialCreate {
  entidade: DocumentoEntidade;
  entidade_id: number;
  tipo_documento: string;
  descricao?: string | null;
  nome_arquivo: string;
  content_type: string;
  s3_key: string;
  bucket_s3?: string | null;
  data_emissao?: string | null;
  data_validade?: string | null;
}

export interface DocumentoOficialUpdate {
  descricao?: string | null;
  data_emissao?: string | null;
  data_validade?: string | null;
  status?: DocumentoStatus | null;
}
