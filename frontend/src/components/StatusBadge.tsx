import { Tag } from 'antd';

/**
 * Colour map for every known status value across all backend enums.
 * Grouped by semantic meaning so colours stay consistent.
 */
const STATUS_COLOR_MAP: Record<string, string> = {
  // ── Positive / active ──
  DISPONIVEL: 'green',
  APROVADA: 'green',
  APROVADO: 'green',
  ATIVO: 'green',
  LIBERADA: 'green',
  CONCLUIDA: 'cyan',
  CONCLUIDO: 'cyan',
  RECEBIDO: 'green',
  FATURADO: 'blue',

  // ── In-progress / neutral ──
  EM_USO: 'blue',
  EM_ANALISE: 'processing',
  EM_EXECUCAO: 'processing',
  EM_PREENCHIMENTO: 'processing',
  EM_FATURAMENTO: 'processing',
  EM_MANUTENCAO: 'orange',
  EM_CHECKLIST: 'purple',
  CARREGANDO: 'geekblue',
  PLANEJADA: 'geekblue',
  AGENDADA: 'geekblue',

  // ── Draft / pending ──
  RASCUNHO: 'default',
  PENDENTE: 'gold',

  // ── Warning / medium ──
  MEDIA: 'orange',
  PAUSADA: 'orange',
  SUBSTITUIDO: 'orange',
  VENCIDO: 'volcano',

  // ── Negative / blocked ──
  BLOQUEADO: 'red',
  INATIVO: 'default',
  REPROVADA: 'red',
  REPROVADO: 'red',
  DESCARTADA: 'red',
  REJEITADA: 'red',
  CANCELADA: 'red',
  CANCELADO: 'red',

  // ── Severity / priority ──
  BAIXA: 'green',
  ALTA: 'orange',
  CRITICA: 'red',

  // ── Encerramento ──
  ENCERRADA_TECNICAMENTE: 'purple',
  ENCERRADA_FINANCEIRAMENTE: 'purple',
};

/** Human-readable labels (replace underscores with spaces, title-case). */
function formatLabel(status: string): string {
  return status
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export interface StatusBadgeProps {
  /** The raw status string (e.g. "EM_EXECUCAO"). */
  status: string;
  /** Optional override — ignored if the status is already in the colour map. */
  color?: string;
}

export default function StatusBadge({ status, color }: StatusBadgeProps) {
  const resolvedColor = STATUS_COLOR_MAP[status] ?? color ?? 'default';
  return <Tag color={resolvedColor}>{formatLabel(status)}</Tag>;
}
