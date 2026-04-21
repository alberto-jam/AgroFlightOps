"""Pydantic schemas for OrdemServico entity."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import OrdemServicoStatus, Prioridade


class OrdemServicoBase(BaseModel):
    cliente_id: int
    propriedade_id: int
    talhao_id: int
    cultura_id: int
    tipo_aplicacao: str = Field(..., max_length=120)
    prioridade: Prioridade
    descricao: str | None = None
    data_prevista: date


class OrdemServicoCreate(OrdemServicoBase):
    pass


class OrdemServicoUpdate(BaseModel):
    tipo_aplicacao: str | None = Field(None, max_length=120)
    prioridade: Prioridade | None = None
    descricao: str | None = None
    data_prevista: date | None = None


class OrdemServicoTransicao(BaseModel):
    status_novo: OrdemServicoStatus
    motivo: str | None = None


class OrdemServicoResponse(OrdemServicoBase):
    id: int
    codigo: str
    status: OrdemServicoStatus
    motivo_rejeicao: str | None
    motivo_cancelamento: str | None
    criado_por: int
    aprovado_por: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HistoricoStatusOSResponse(BaseModel):
    id: int
    ordem_servico_id: int
    status_anterior: str | None
    status_novo: str
    motivo: str | None
    alterado_por: int
    created_at: datetime

    model_config = {"from_attributes": True}
