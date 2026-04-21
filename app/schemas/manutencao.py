"""Pydantic schemas for Manutencao entity."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ManutencaoBase(BaseModel):
    drone_id: int
    tipo: str = Field(..., max_length=100)
    descricao: str | None = None
    data_manutencao: date
    proxima_manutencao: date | None = None
    horas_na_data: Decimal | None = Field(None, ge=0)


class ManutencaoCreate(ManutencaoBase):
    pass


class ManutencaoUpdate(BaseModel):
    tipo: str | None = Field(None, max_length=100)
    descricao: str | None = None
    data_manutencao: date | None = None
    proxima_manutencao: date | None = None
    horas_na_data: Decimal | None = Field(None, ge=0)


class ManutencaoResponse(ManutencaoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
