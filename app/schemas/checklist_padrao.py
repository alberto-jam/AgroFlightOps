"""Pydantic schemas for ItemChecklistPadrao entity."""

from datetime import datetime

from pydantic import BaseModel, Field


class ItemChecklistPadraoBase(BaseModel):
    nome_item: str = Field(..., max_length=200)
    descricao: str | None = None
    obrigatorio: bool = True
    ordem_exibicao: int = Field(default=0, ge=0)


class ItemChecklistPadraoCreate(ItemChecklistPadraoBase):
    pass


class ItemChecklistPadraoUpdate(BaseModel):
    nome_item: str | None = Field(None, max_length=200)
    descricao: str | None = None
    obrigatorio: bool | None = None
    ordem_exibicao: int | None = Field(None, ge=0)


class ItemChecklistPadraoResponse(ItemChecklistPadraoBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
