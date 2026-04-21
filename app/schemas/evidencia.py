"""Pydantic schemas for Evidencia entity."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class EvidenciaBase(BaseModel):
    missao_id: int
    nome_arquivo: str = Field(..., max_length=255)
    url_arquivo: str | None = None
    tipo_arquivo: str | None = Field(None, max_length=80)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)


class EvidenciaCreate(EvidenciaBase):
    pass


class EvidenciaResponse(EvidenciaBase):
    id: int
    enviado_por: int
    created_at: datetime

    model_config = {"from_attributes": True}
