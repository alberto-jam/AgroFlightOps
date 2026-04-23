"""Pydantic schemas for Talhao entity."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class TalhaoBase(BaseModel):
    propriedade_id: int
    nome: str = Field(..., max_length=150)
    area_hectares: Decimal = Field(..., ge=0)
    cultura_id: int
    observacoes: str | None = None
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    ponto_referencia: str | None = Field(None, max_length=255)
    geojson: dict[str, Any] | None = None


class TalhaoCreate(TalhaoBase):
    pass


class TalhaoUpdate(BaseModel):
    propriedade_id: int | None = None
    nome: str | None = Field(None, max_length=150)
    area_hectares: Decimal | None = Field(None, ge=0)
    cultura_id: int | None = None
    observacoes: str | None = None
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    ponto_referencia: str | None = Field(None, max_length=255)
    geojson: dict[str, Any] | None = None
    ativo: bool | None = None


class TalhaoResponse(TalhaoBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
