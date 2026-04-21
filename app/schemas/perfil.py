"""Pydantic schemas for Perfil entity."""

from datetime import datetime

from pydantic import BaseModel, Field


class PerfilBase(BaseModel):
    nome: str = Field(..., max_length=80)
    descricao: str | None = None


class PerfilCreate(PerfilBase):
    pass


class PerfilUpdate(BaseModel):
    nome: str | None = Field(None, max_length=80)
    descricao: str | None = None


class PerfilResponse(PerfilBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
