/** Enum string union types matching backend Python enums. */

export type DroneStatus =
  | 'DISPONIVEL'
  | 'EM_USO'
  | 'EM_MANUTENCAO'
  | 'BLOQUEADO'
  | 'INATIVO';

export type BateriaStatus =
  | 'DISPONIVEL'
  | 'EM_USO'
  | 'CARREGANDO'
  | 'REPROVADA'
  | 'DESCARTADA';

export type OrdemServicoStatus =
  | 'RASCUNHO'
  | 'EM_ANALISE'
  | 'APROVADA'
  | 'REJEITADA'
  | 'CANCELADA';

export type Prioridade =
  | 'BAIXA'
  | 'MEDIA'
  | 'ALTA'
  | 'CRITICA';

export type MissaoStatus =
  | 'RASCUNHO'
  | 'PLANEJADA'
  | 'AGENDADA'
  | 'EM_CHECKLIST'
  | 'LIBERADA'
  | 'EM_EXECUCAO'
  | 'PAUSADA'
  | 'CONCLUIDA'
  | 'CANCELADA'
  | 'ENCERRADA_TECNICAMENTE'
  | 'ENCERRADA_FINANCEIRAMENTE';

export type ChecklistStatusGeral =
  | 'PENDENTE'
  | 'EM_PREENCHIMENTO'
  | 'CONCLUIDO'
  | 'REPROVADO'
  | 'APROVADO';

export type ItemChecklistStatus =
  | 'PENDENTE'
  | 'APROVADO'
  | 'REPROVADO'
  | 'NAO_APLICAVEL';

export type Severidade =
  | 'BAIXA'
  | 'MEDIA'
  | 'ALTA'
  | 'CRITICA';

export type FinanceiroStatus =
  | 'PENDENTE'
  | 'EM_FATURAMENTO'
  | 'FATURADO'
  | 'RECEBIDO'
  | 'CANCELADO';

export type DocumentoEntidade =
  | 'DRONE'
  | 'MANUTENCAO'
  | 'USUARIO'
  | 'CLIENTE'
  | 'PROPRIEDADE'
  | 'INSUMO'
  | 'MISSAO';

export type DocumentoStatus =
  | 'ATIVO'
  | 'SUBSTITUIDO'
  | 'VENCIDO'
  | 'INATIVO';
