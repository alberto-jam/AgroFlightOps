"""Pydantic schemas for Propriedade entity."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PropriedadeBase(BaseModel):
    cliente_id: int
    nome: str = Field(..., max_length=200)
    endereco: str | None = Field(None, max_length=255)
    numero: str | None = Field(None, max_length=20)
    complemento: str | None = Field(None, max_length=120)
    bairro: str | None = Field(None, max_length=120)
    municipio: str = Field(..., max_length=120)
    estado: str = Field(..., max_length=2)
    cep: str | None = Field(None, max_length=12)
    localizacao_descritiva: str | None = None
    referencia_local: str | None = Field(None, max_length=255)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    area_total: Decimal = Field(..., ge=0)


class PropriedadeCreate(PropriedadeBase):
    pass


class PropriedadeUpdate(BaseModel):
    nome: str | None = Field(None, max_length=200)
    endereco: str | None = Field(None, max_length=255)
    numero: str | None = Field(None, max_length=20)
    complemento: str | None = Field(None, max_length=120)
    bairro: str | None = Field(None, max_length=120)
    municipio: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=2)
    cep: str | None = Field(None, max_length=12)
    localizacao_descritiva: str | None = None
    referencia_local: str | None = Field(None, max_length=255)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    area_total: Decimal | None = Field(None, ge=0)


class PropriedadeResponse(PropriedadeBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
