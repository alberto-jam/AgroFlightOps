/** TypeScript interfaces for Auditoria entity matching Pydantic schemas. */

export interface AuditoriaResponse {
  id: number;
  entidade: string;
  entidade_id: number;
  acao: string;
  valor_anterior: Record<string, unknown> | null;
  valor_novo: Record<string, unknown> | null;
  usuario_id: number;
  created_at: string;
}
