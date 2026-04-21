/** Barrel export for all TypeScript types. */

// Common
export type { PaginatedResponse } from './common';

// Enums
export type {
  DroneStatus,
  BateriaStatus,
  OrdemServicoStatus,
  Prioridade,
  MissaoStatus,
  ChecklistStatusGeral,
  ItemChecklistStatus,
  Severidade,
  FinanceiroStatus,
  DocumentoEntidade,
  DocumentoStatus,
} from './enums';

// Auth (re-export existing types)
export type {
  Perfil,
  User,
  AuthState,
  LoginRequest,
  LoginResponse,
  JwtPayload,
} from './auth';

// Entities
export type { PerfilResponse, PerfilCreate, PerfilUpdate } from './perfil';
export type { UsuarioResponse, UsuarioCreate, UsuarioUpdate } from './usuario';
export type { ClienteResponse, ClienteCreate, ClienteUpdate } from './cliente';
export type { PropriedadeResponse, PropriedadeCreate, PropriedadeUpdate } from './propriedade';
export type { TalhaoResponse, TalhaoCreate, TalhaoUpdate } from './talhao';
export type { CulturaResponse, CulturaCreate, CulturaUpdate } from './cultura';
export type { DroneResponse, DroneCreate, DroneUpdate } from './drone';
export type { BateriaResponse, BateriaCreate, BateriaUpdate } from './bateria';
export type { InsumoResponse, InsumoCreate, InsumoUpdate } from './insumo';
export type {
  OrdemServicoResponse,
  OrdemServicoCreate,
  OrdemServicoUpdate,
  OrdemServicoTransicao,
  HistoricoStatusOSResponse,
} from './ordem-servico';
export type {
  MissaoResponse,
  MissaoCreate,
  MissaoUpdate,
  MissaoRegistroExecucao,
  MissaoTransicao,
  HistoricoStatusMissaoResponse,
} from './missao';
export type {
  ChecklistMissaoResponse,
  ItemChecklistMissaoResponse,
  ItemChecklistMissaoUpdate,
} from './checklist';
export type { OcorrenciaResponse, OcorrenciaCreate } from './ocorrencia';
export type { EvidenciaResponse, EvidenciaCreate } from './evidencia';
export type { ManutencaoResponse, ManutencaoCreate, ManutencaoUpdate } from './manutencao';
export type {
  DocumentoOficialResponse,
  DocumentoOficialCreate,
  DocumentoOficialUpdate,
} from './documento-oficial';
export type { FinanceiroMissaoResponse, FinanceiroMissaoUpdate } from './financeiro';
export type { AuditoriaResponse } from './auditoria';
export type {
  RelatorioFiltro,
  MissoesPorStatusItem,
  MissoesPorStatusResponse,
  AreaPorClienteItem,
  AreaPorClienteResponse,
  FinanceiroResumoResponse,
  UtilizacaoDroneItem,
  UtilizacaoDroneResponse,
} from './relatorio';
export type {
  ReservaInsumoResponse,
  ReservaInsumoCreate,
  ConsumoInsumoMissaoResponse,
  ConsumoInsumoMissaoCreate,
} from './reserva-insumo';
export type { MissaoBateriaResponse, MissaoBateriaCreate } from './missao-bateria';
export type {
  TipoOcorrenciaResponse,
  TipoOcorrenciaCreate,
  TipoOcorrenciaUpdate,
} from './tipo-ocorrencia';
export type {
  ItemChecklistPadraoResponse,
  ItemChecklistPadraoCreate,
  ItemChecklistPadraoUpdate,
} from './checklist-padrao';
