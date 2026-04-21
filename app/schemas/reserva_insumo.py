"""Pydantic schemas for ReservaInsumo and ConsumoInsumoMissao."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ReservaInsumoBase(BaseModel):
    missao_id: int
    insumo_id: int
    quantidade_prevista: Decimal = Field(..., ge=0)
    unidade_medida: str = Field(..., max_length=30)
    justificativa_excesso: str | None = None


class ReservaInsumoCreate(ReservaInsumoBase):
    pass


class ReservaInsumoResponse(ReservaInsumoBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsumoInsumoMissaoBase(BaseModel):
    missao_id: int
    insumo_id: int
    quantidade_realizada: Decimal = Field(..., ge=0)
    unidade_medida: str = Field(..., max_length=30)
    observacoes: str | None = None
    justificativa_excesso: str | None = None


class ConsumoInsumoMissaoCreate(ConsumoInsumoMissaoBase):
    pass


class ConsumoInsumoMissaoResponse(ConsumoInsumoMissaoBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
