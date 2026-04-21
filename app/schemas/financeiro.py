"""Pydantic schemas for FinanceiroMissao entity."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import FinanceiroStatus


class FinanceiroMissaoBase(BaseModel):
    custo_estimado: Decimal = Field(default=Decimal("0"), ge=0)
    custo_realizado: Decimal = Field(default=Decimal("0"), ge=0)
    valor_faturado: Decimal = Field(default=Decimal("0"), ge=0)
    status_financeiro: FinanceiroStatus = FinanceiroStatus.PENDENTE
    observacoes: str | None = None


class FinanceiroMissaoUpdate(BaseModel):
    custo_estimado: Decimal | None = Field(None, ge=0)
    custo_realizado: Decimal | None = Field(None, ge=0)
    valor_faturado: Decimal | None = Field(None, ge=0)
    status_financeiro: FinanceiroStatus | None = None
    observacoes: str | None = None


class FinanceiroMissaoResponse(FinanceiroMissaoBase):
    id: int
    missao_id: int
    fechado_por: int | None
    fechado_em: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
