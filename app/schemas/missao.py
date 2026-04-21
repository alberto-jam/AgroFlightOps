"""Pydantic schemas for Missao entity."""

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import MissaoStatus


class MissaoBase(BaseModel):
    ordem_servico_id: int
    piloto_id: int
    tecnico_id: int | None = None
    drone_id: int
    data_agendada: date
    hora_agendada: time
    area_prevista: Decimal = Field(..., ge=0)
    volume_previsto: Decimal = Field(..., ge=0)
    janela_operacional: str | None = Field(None, max_length=255)
    restricoes: str | None = None
    observacoes_planejamento: str | None = None
    latitude_operacao: Decimal | None = Field(None, ge=-90, le=90)
    longitude_operacao: Decimal | None = Field(None, ge=-180, le=180)
    endereco_operacao: str | None = Field(None, max_length=255)
    referencia_operacao: str | None = Field(None, max_length=255)


class MissaoCreate(MissaoBase):
    pass


class MissaoUpdate(BaseModel):
    piloto_id: int | None = None
    tecnico_id: int | None = None
    drone_id: int | None = None
    data_agendada: date | None = None
    hora_agendada: time | None = None
    area_prevista: Decimal | None = Field(None, ge=0)
    area_realizada: Decimal | None = Field(None, ge=0)
    volume_previsto: Decimal | None = Field(None, ge=0)
    volume_realizado: Decimal | None = Field(None, ge=0)
    janela_operacional: str | None = Field(None, max_length=255)
    restricoes: str | None = None
    observacoes_planejamento: str | None = None
    observacoes_execucao: str | None = None
    latitude_operacao: Decimal | None = Field(None, ge=-90, le=90)
    longitude_operacao: Decimal | None = Field(None, ge=-180, le=180)
    endereco_operacao: str | None = Field(None, max_length=255)
    referencia_operacao: str | None = Field(None, max_length=255)


class MissaoRegistroExecucao(BaseModel):
    area_realizada: Decimal | None = Field(None, ge=0)
    volume_realizado: Decimal | None = Field(None, ge=0)
    observacoes_execucao: str | None = None


class MissaoTransicao(BaseModel):
    status_novo: MissaoStatus
    motivo: str | None = None


class MissaoResponse(BaseModel):
    id: int
    codigo: str
    ordem_servico_id: int
    piloto_id: int
    tecnico_id: int | None
    drone_id: int
    data_agendada: date
    hora_agendada: time
    area_prevista: Decimal
    area_realizada: Decimal | None
    volume_previsto: Decimal
    volume_realizado: Decimal | None
    janela_operacional: str | None
    restricoes: str | None
    observacoes_planejamento: str | None
    observacoes_execucao: str | None
    status: MissaoStatus
    latitude_operacao: Decimal | None
    longitude_operacao: Decimal | None
    endereco_operacao: str | None
    referencia_operacao: str | None
    iniciado_em: datetime | None
    finalizado_em: datetime | None
    encerrado_tecnicamente_em: datetime | None
    encerrado_financeiramente_em: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HistoricoStatusMissaoResponse(BaseModel):
    id: int
    missao_id: int
    status_anterior: str | None
    status_novo: str
    motivo: str | None
    alterado_por: int
    created_at: datetime

    model_config = {"from_attributes": True}
