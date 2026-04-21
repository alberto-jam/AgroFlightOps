"""Pydantic schemas for TipoOcorrencia entity."""

from datetime import datetime

from pydantic import BaseModel, Field


class TipoOcorrenciaBase(BaseModel):
    nome: str = Field(..., max_length=120)
    descricao: str | None = None


class TipoOcorrenciaCreate(TipoOcorrenciaBase):
    pass


class TipoOcorrenciaUpdate(BaseModel):
    nome: str | None = Field(None, max_length=120)
    descricao: str | None = None


class TipoOcorrenciaResponse(TipoOcorrenciaBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
