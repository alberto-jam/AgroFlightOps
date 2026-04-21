"""Pydantic schemas for Cultura entity."""

from datetime import datetime

from pydantic import BaseModel, Field


class CulturaBase(BaseModel):
    nome: str = Field(..., max_length=120)
    descricao: str | None = None


class CulturaCreate(CulturaBase):
    pass


class CulturaUpdate(BaseModel):
    nome: str | None = Field(None, max_length=120)
    descricao: str | None = None


class CulturaResponse(CulturaBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
