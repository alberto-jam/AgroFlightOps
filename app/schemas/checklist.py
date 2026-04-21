"""Pydantic schemas for ChecklistMissao and ItemChecklistMissao."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ChecklistStatusGeral, ItemChecklistStatus


class ItemChecklistMissaoBase(BaseModel):
    nome_item: str = Field(..., max_length=200)
    obrigatorio: bool = True
    status_item: ItemChecklistStatus = ItemChecklistStatus.PENDENTE
    observacao: str | None = None


class ItemChecklistMissaoUpdate(BaseModel):
    status_item: ItemChecklistStatus
    observacao: str | None = None


class ItemChecklistMissaoResponse(ItemChecklistMissaoBase):
    id: int
    checklist_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChecklistMissaoResponse(BaseModel):
    id: int
    missao_id: int
    status_geral: ChecklistStatusGeral
    preenchido_por: int
    revisado_por: int | None
    preenchido_em: datetime
    revisado_em: datetime | None
    observacoes: str | None
    itens: list[ItemChecklistMissaoResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
