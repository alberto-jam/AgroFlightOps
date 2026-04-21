"""Enum definitions matching DDL CHECK constraints."""

from enum import Enum


class DroneStatus(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    EM_USO = "EM_USO"
    EM_MANUTENCAO = "EM_MANUTENCAO"
    BLOQUEADO = "BLOQUEADO"
    INATIVO = "INATIVO"


class BateriaStatus(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    EM_USO = "EM_USO"
    CARREGANDO = "CARREGANDO"
    REPROVADA = "REPROVADA"
    DESCARTADA = "DESCARTADA"


class OrdemServicoStatus(str, Enum):
    RASCUNHO = "RASCUNHO"
    EM_ANALISE = "EM_ANALISE"
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"
    CANCELADA = "CANCELADA"


class Prioridade(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class MissaoStatus(str, Enum):
    RASCUNHO = "RASCUNHO"
    PLANEJADA = "PLANEJADA"
    AGENDADA = "AGENDADA"
    EM_CHECKLIST = "EM_CHECKLIST"
    LIBERADA = "LIBERADA"
    EM_EXECUCAO = "EM_EXECUCAO"
    PAUSADA = "PAUSADA"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"
    ENCERRADA_TECNICAMENTE = "ENCERRADA_TECNICAMENTE"
    ENCERRADA_FINANCEIRAMENTE = "ENCERRADA_FINANCEIRAMENTE"


class ChecklistStatusGeral(str, Enum):
    PENDENTE = "PENDENTE"
    EM_PREENCHIMENTO = "EM_PREENCHIMENTO"
    CONCLUIDO = "CONCLUIDO"
    REPROVADO = "REPROVADO"
    APROVADO = "APROVADO"


class ItemChecklistStatus(str, Enum):
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"
    NAO_APLICAVEL = "NAO_APLICAVEL"


class Severidade(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class FinanceiroStatus(str, Enum):
    PENDENTE = "PENDENTE"
    EM_FATURAMENTO = "EM_FATURAMENTO"
    FATURADO = "FATURADO"
    RECEBIDO = "RECEBIDO"
    CANCELADO = "CANCELADO"


class DocumentoEntidade(str, Enum):
    DRONE = "DRONE"
    MANUTENCAO = "MANUTENCAO"
    USUARIO = "USUARIO"
    CLIENTE = "CLIENTE"
    PROPRIEDADE = "PROPRIEDADE"
    INSUMO = "INSUMO"
    MISSAO = "MISSAO"


class DocumentoStatus(str, Enum):
    ATIVO = "ATIVO"
    SUBSTITUIDO = "SUBSTITUIDO"
    VENCIDO = "VENCIDO"
    INATIVO = "INATIVO"
