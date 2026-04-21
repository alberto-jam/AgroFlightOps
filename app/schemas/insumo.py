"""Pydantic schemas for Insumo entity."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class InsumoBase(BaseModel):
    nome: str = Field(..., max_length=200)
    fabricante: str | None = Field(None, max_length=120)
    unidade_medida: str = Field(..., max_length=30)
    saldo_atual: Decimal = Field(default=Decimal("0"), ge=0)
    lote: str | None = Field(None, max_length=100)
    validade: date | None = None


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    nome: str | None = Field(None, max_length=200)
    fabricante: str | None = Field(None, max_length=120)
    unidade_medida: str | None = Field(None, max_length=30)
    saldo_atual: Decimal | None = Field(None, ge=0)
    lote: str | None = Field(None, max_length=100)
    validade: date | None = None


class InsumoResponse(InsumoBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
