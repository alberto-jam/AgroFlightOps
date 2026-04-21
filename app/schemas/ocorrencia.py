"""Pydantic schemas for Ocorrencia entity."""

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Severidade


class OcorrenciaBase(BaseModel):
    missao_id: int
    tipo_ocorrencia_id: int
    descricao: str
    severidade: Severidade


class OcorrenciaCreate(OcorrenciaBase):
    pass


class OcorrenciaResponse(OcorrenciaBase):
    id: int
    registrada_por: int
    registrada_em: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
